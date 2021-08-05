# workaround to get imports working with the script like approach
# since this is more of a "script" an actual module/pkg
# structure is overkill, just wanted to add some automatic
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from main import Workspace, slacktoken

def test_workspace_connect():
    
    # create example workspace
    example = Workspace(token=slacktoken())
    
    # ensure there's channels and users
    assert example.channel_dict
    assert example.users
