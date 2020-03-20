import sys
from github import Github

# Getting the command line arguments as inputs
token = sys.argv[1]
version = sys.argv[2]
sha256 = sys.argv[3]
url = sys.argv[4]

sha256_replacement = '  sha256 "'+sha256+'"\n'

url_replacement = '  url "'+url+'"\n'

updated_ballerina_rb = ""

g = Github(token)

# Getting an instance of the Homebrew/homebrew-core repo
#TODO: Change this to homebrew_user = g.get_user("Homebrew") in production usage
homebrew_user = g.get_user("Homebrew")
homebrew_core_repo = homebrew_user.get_repo("homebrew-core")

# Reading the current ballerina.rb Formula file and updating it.
ballerina_rb_file = homebrew_core_repo.get_contents("Formula/ballerina.rb")

for line in ballerina_rb_file.decoded_content.decode("utf-8").split("\n"):
    updated_line = line
    if(line.startswith('  url "')):
        updated_line = url_replacement
    elif(line.startswith('  sha256 "')):
        updated_line = sha256_replacement

    updated_ballerina_rb += updated_line+"\n"

updated_ballerina_rb = updated_ballerina_rb.rstrip()

commit_msg = "ballerina "+str(version)


current_user = g.get_user()
current_user_login = current_user.login

# Commiting and pushing the updated ballerina.rb file to the current users forked homebrew-core repo
# [Important]The user who provides the access token also should fork the Homebrew/homebrew-core repo in order for this to work

repo = g.get_repo(current_user_login+"/homebrew-core")
contents = repo.get_contents("Formula/ballerina.rb", ref="master")
update = repo.update_file(contents.path, commit_msg, updated_ballerina_rb, contents.sha, branch="master")


# Opening a PR in Homebrew/homebrew-core repo

body = '''
 - [x] Have you followed the [guidelines for contributing](https://github.com/Homebrew/homebrew-core/blob/master/CONTRIBUTING.md)?
 - [x] Have you checked that there aren't other open [pull requests](https://github.com/Homebrew/homebrew-core/pulls) for the same formula update/change?
 - [x] Have you built your formula locally with ```brew install --build-from-source <formula>```, where ```<formula>``` is the name of the formula you're submitting?
 - [x] Is your test running fine ```brew test <formula>```, where ```<formula>``` is the name of the formula you're submitting?
 - [x] Does your build pass ```brew audit --strict <formula>``` (after doing ```brew install <formula>```)?
'''

pr = homebrew_core_repo.create_pull(title=commit_msg, body=body, base="master", head='{}:{}'.format(current_user_login, 'master'))
