import hashlib
import json
import uuid
from unittest import mock

import google.auth
import httpx
import pytest
from django.test.utils import override_settings

from person.models import CV, User

PDF = b'%PDF-1.4 fake cv for tests'
DI_TEXT = 'John Doe\njohn@example.com\nPython developer at Acme'

PROFILE = {
    'emails': [{'value': 'john@example.com', 'score': 1.0}],
    'phones': [], 'bio': [], 'links': [],
    'first_name': {'value': 'John', 'score': 1.0},
    'last_name': {'value': 'Doe', 'score': 1.0},
    'location_city': {'value': 'Minsk', 'score': 0.9},
    'location_country': {'value': 'BY', 'score': 0.9},
    'birthday': {'value': '', 'score': 0.0},
    'positions': [], 'education_raw': [], 'interests': [], 'languages': [],
}
SKILLS = {
    'soft_skills': [{'name': 'Communication', 'score': 0.8, 'justification': 'led standups'}],
    'hard_skills': [{'name': 'Python', 'score': 0.9, 'justification': 'built services'}],
}
EXPERIENCES = {'experiences': [{
    'company': {'value': 'Acme', 'score': 1.0, 'justification': 'header'},
    'role': {'value': 'Developer', 'score': 1.0, 'justification': 'header'},
    'date_start': {'value': '2020-01', 'score': 0.9, 'justification': 'dates line'},
    'date_finish': {'value': 'Present', 'score': 0.9, 'justification': 'dates line'},
    'product': {'value': '', 'score': 0.0, 'justification': ''},
    'area': {'value': '', 'score': 0.0, 'justification': ''},
    'description': {'value': 'Built Python services at Acme.', 'score': 0.9},
    'soft_skills': [], 'hard_skills': [],
}]}


RESULTS = {'CVProfile': PROFILE, 'CVSkills': SKILLS, 'CVExperiences': EXPERIENCES}


@pytest.fixture
def cv(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # md5_dir is CWD-relative
    # BASE_DIR=tmp_path keeps task_logs/ out of the repo and hides service-account.json so jobs take the ADC branch
    with override_settings(MEDIA_ROOT=tmp_path, BASE_DIR=tmp_path):
        user = User.objects.create(username='u_%s' % uuid.uuid4().hex[:8])
        md5 = hashlib.md5(PDF).hexdigest()
        name = f'cv/{md5[:2]}/{md5[2:4]}/{md5[4:6]}/{md5}/{md5}.pdf'
        (tmp_path / name).parent.mkdir(parents=True)
        (tmp_path / name).write_bytes(PDF)
        cv = CV(user=user, status=9)
        cv.file.name = name  # bypass storage save: md5_upload_to yields absolute paths, rejected by Django 6
        cv.save()
        yield cv


@pytest.fixture
def gcp(monkeypatch):
    creds = mock.Mock(token='fake-token')
    monkeypatch.setattr(google.auth, 'default', lambda scopes=None: (creds, 'test-project'))

    def fake_post(url, headers=None, json=None, timeout=None):  # Document AI, used by stage1job
        return mock.Mock(status_code=200, **{'json.return_value': {'document': {'text': DI_TEXT}}})

    monkeypatch.setattr(httpx, 'post', fake_post)
    # llmJob calls this to get the extracted phase; stub it instead of faking the whole
    # Vertex/OpenAI call chain, which is llm.caller's concern, not CV's.
    monkeypatch.setattr('person.models.run_model', lambda model, prompt, schema: json.dumps(RESULTS[schema.__name__]))


def test_stages(cv, gcp):
    CV.stage1job(cv.id)
    cv.refresh_from_db()
    assert cv.error is None
    assert (cv.md5_dir / f'{cv.md5}.txt').read_text() == DI_TEXT
    assert json.loads((cv.md5_dir / f'{cv.md5}.json').read_text())['document']['text'] == DI_TEXT
    assert cv.file_di_text.exists() and cv.file_di_text.read_text() == DI_TEXT
    assert cv.file_di_json.exists()
    assert cv.status == 19

    CV.llmJob(cv.id, new_status=29, phase='profile')
    cv.refresh_from_db()
    assert cv.error is None
    assert cv.status == 29
    assert cv.summary_llm_json['first_name']['value'] == 'John'
    assert (cv.md5_dir / f'{cv.md5}.profile.json').is_file()

    CV.llmJob(cv.id, new_status=39, phase='skills')
    cv.refresh_from_db()
    assert cv.error is None
    assert cv.status == 39
    assert cv.as_json()['soft_skills'][0]['name'] == 'Communication'
    assert cv.as_json()['hard_skills'][0]['name'] == 'Python'
    assert cv.as_json()['first_name'] == 'John'  # merge kept the profile
    assert (cv.md5_dir / f'{cv.md5}.skills.json').is_file()

    CV.llmJob(cv.id, new_status=49, phase='experience')
    cv.refresh_from_db()
    assert cv.error is None
    assert cv.status == 49
    assert cv.as_json()['experiences'][0]['company'] == 'Acme'
    assert (cv.md5_dir / f'{cv.md5}.experience.json').is_file()

    fresh = CV.objects.get(id=cv.id)
    assert fresh.status == 49 and fresh.error is None
    assert fresh.as_json()['first_name'] == 'John'
    assert fresh.as_json()['soft_skills'][0]['name'] == 'Communication'
    assert fresh.as_json()['experiences'][0]['company'] == 'Acme'
