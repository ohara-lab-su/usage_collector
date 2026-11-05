import csv
from usage_collector import CSVHistory, PyPIAnalytics, GA4Analytics

def test_domain_analytics(tmp_path):
    for source, name, fields, row in [
        ('pypi','overall',['date','package','category','downloads'],['2026-11-01','pkg','without_mirrors','3']),
        ('ga4','countries',['date','country','sessions','activeUsers'],['2026-11-01','Japan','5','4'])]:
        path=tmp_path/source/(name+'.csv'); path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('w',newline='') as f:
            w=csv.writer(f); w.writerow(fields); w.writerow(row)
    h=CSVHistory(tmp_path)
    assert PyPIAnalytics(h).downloads()[('pkg','without_mirrors')]['2026-11-01']==3
    assert GA4Analytics(h).report('countries')[('Japan',)]['2026-11-01']==5
