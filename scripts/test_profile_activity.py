import unittest
from datetime import datetime, timezone
from update_activity import collect, markdown_text, svg

class ActivityTests(unittest.TestCase):
    def test_private_forks_bots_and_duplicate_shas_are_excluded(self):
        now=datetime(2026,10,31,18,tzinfo=timezone.utc)
        repo={'full_name':'brahian-mesa/project','pushed_at':'2026-10-31T12:00:00Z'}
        calls=[]
        row={'sha':'a'*40,'author':{'login':'brahian-mesa'},'html_url':'https://github.com/brahian-mesa/project/commit/'+'a'*40,
             'commit':{'author':{'date':'2026-10-31T12:00:00Z'},'message':'Fix <script>\nbody'}}
        def request(path):
            calls.append(path)
            if path.startswith('users/'):
                return [repo,{**repo,'full_name':'brahian-mesa/private','private':True},
                        {**repo,'full_name':'brahian-mesa/fork','fork':True}]
            return [row,row,{**row,'sha':'b'*40,'author':{'login':'github-actions[bot]'}}]
        data=collect(now,request)
        self.assertEqual(len(data['commits']),1)
        self.assertEqual(data['from'],'2026-10-04')
        self.assertFalse(any('/private/' in path or '/fork/' in path for path in calls))
        self.assertEqual(data['commits'][0]['subject'],'Fix <script>')

    def test_commit_subjects_cannot_inject_readme_markup(self):
        result=markdown_text('[click](bad) <img> **bold** `code`')
        self.assertIn(r'\[click\]',result)
        self.assertIn(r'\<img\>',result)
        self.assertIn(r'\*\*bold\*\*',result)

    def test_empty_window_renders_without_fake_counts(self):
        image=svg({'from':'2026-10-04','through':'2026-10-31','commits':[]})
        self.assertIn('0 commits / 28 días',image)
        self.assertEqual(image.count('<rect x='),28)

if __name__=='__main__':
    unittest.main()
