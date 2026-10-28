
**General Notes**

An `onlinecourse` app has already been provided in this repo upon which you will be adding a new assesement feature.

- If you want to develop the final project on Theia hosted by [IBM Developer Skills Network](https://labs.cognitiveclass.ai/), you will need to create the same project structure on Theia workspace and save it everytime you close the browser
- Or you could develop the final project locally by setting up your own Python runtime and IDE
- Hints for the final project are left on source code files
- You may choose any cloud platform for deployment (default is IBM Cloud Foundry)
- Depends on your deployment, you may choose any SQL database Django supported such as SQLite3, PostgreSQL, and MySQL (default is SQLite3)

**ER Diagram**
For your reference, we have prepared the ER diagram design for the new assesement feature.

![Onlinecourse ER Diagram](https://github.com/ibm-developer-skills-network/final-cloud-app-with-database/blob/master/static/media/course_images/onlinecourse_app_er.png)


**Assessment feature (final project)**

The `onlinecourse` app now includes exam models (`Question`, `Choice`, `Submission`), the exam form on the course details page, and the `submit` / `show_exam_result` views with an exam result page.

Run it locally:

```bash
python -m venv .venv
.venv/Scripts/activate        # Windows (use source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo    # demo course, exam and users (see onlinecourse/management/commands/seed_demo.py)
python manage.py runserver
```

Open http://127.0.0.1:8000/onlinecourse/ and the admin site at http://127.0.0.1:8000/admin/.
