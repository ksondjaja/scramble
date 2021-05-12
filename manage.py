import os
from app import create_app, db
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

# Create the application with development configuration
app = create_app('production')

# Create the command line manager
manager = Manager(app)

# Create the database migrate 
# TODO: Check if we can move this to app/__init__
migrate = Migrate(app, db, compare_type=True)
manager.add_command('db', MigrateCommand)

@manager.command
def deploy():
    '''
    Run deployment tasks
    '''
    from flask_migrate import upgrade 
    from app.models.user import User

    # Migrate database to the latest version
    upgrade()
    

if __name__ == "__main__":
    manager.run()
