# Development Journey
<font color="red"> This is currently in draft. It is a dynamic document until the project is complete.</font>
## Project Genesis
- Initial problem statement <font color="red">Draft</font>
- Why this solution was chosen <font color="red">Draft</font>

## Key Development Stages
1. Initial Data Validation
   - Challenges faced: lots of manual checking in advance of creating the final script which included looking at the ER Studio database output, log files and print to screen info.
   - Solutions implemented: <font color="red">Draft</font>

2. API Integration
   - Learnings about OpenMetadata API <font color="red">Draft</font>
   - Handling authentication and requests <font color="red">Draft</font>

3. Error Handling and Retry Logic
   - Why it was necessary <font color="red">Draft</font>
   - How it improved script reliability <font color="red">Draft</font>

4. Dry Run Implementation
   - Running simulations and dry runs helped prevent populating OpenMetadata while exploring the data and functionality of the API

5. Unit Testing
   - This was an afterthough while preparing documentation and the folder structure for the repo. A simple unit test exists in the folder structure and is not currently linked to any GitHub actions.

## Challenges and Solutions

- The OpenMetadata SDK was tried though it did not provide the results expected (many error messages) and made the decision to switch to the requests module
- The major challenge was identifying tables through OpenMetadata. The assets in OpenMetadata are only have the service, database and schema to use via the API.
- In order to identify tables to app a list of FQN's that exist within OpenMetadata were pulled to work along side the script
- Initially created simulation scripts and moved to using `--dry-run` for testing
- Batched PATCH requests in 100 with a 2 second delay as to not overwhelm OpenMetadata
- Used metrics in Openshift and sysdig to monitor spikes
- API syntax was a steep learning curve
Because the scripts were created in subfolders of an existing development environment OS realpath was implemented so the script can be run from anywhere in - the directory structure
- Needed to identify duplicate tables
- Tags from IRS do not always match the tags created from ER Studio database


## Future Improvements
- Refactor scripts to run from `main.py` in a sequenced order and have SQL scripts run from python to create CSV's.
- Known limitations of the current implementation <font color="red">Draft</font>

## Lessons Learned
- Start documenting early
- Think of repo/folder structure and documentation ahead of time
- Continuously test and validate
- Think with the end in mind rather than being reactive. Had research been done it would have been discovered earlier that the asset tagging would have needed more than one method

## How to update Python Versions (TL;DR)
- Navigate to the project directory
- `pipenv --rm` (remove old environment)
- Edit Pipfile to change `python_version = "3.10"`
- `pipenv install` (recreate with Python 3.10)
- `pipenv requirements > requirements.txt` (update requirements)
- Test with your scripts
- Clean up any unused dependencies
- Commit and push

## Resources
- [OpenMetadata Slack channel](https://openmetadata.slack.com/archives/C02B6955S4S)
- [OpenMetadata Swagger API documentation](https://docs.open-metadata.org/swagger.html)
- [Claude.ai](https://claude.ai/)