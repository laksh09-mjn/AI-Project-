import sys
sys.path.insert(0, '.')

print('Testing imports...')
import config
print('  config.py        OK')

from backend import data
print('  backend/data.py  OK  --', len(data.RECORDS), 'records loaded')

from backend import detector
print('  backend/detector.py  OK')

from backend import routes
print('  backend/routes.py    OK')

print()
print('Testing AnomalyDetector...')
d = detector.AnomalyDetector(data.RECORDS)
r = d.analyze(data.RECORDS[0])
print('  Record #1  risk_level:', r['risk_level'], ' score:', r['risk_score'], ' Z:', r['z_score'])

print()
print('Testing Flask app factory...')
import app as app_module
flask_app = app_module.create_app()
print('  Flask app created:', flask_app.name)

print()
print('ALL TESTS PASSED -- Run the app with:  python app.py')
