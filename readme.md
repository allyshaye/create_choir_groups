This is a Python script that parses the CSV results of a Google Form completed by each choir member in order to determine what special, end-of-year services they will be performing in December.

Each choir member is assigned to perform twice: their regularly scheduled weekend performance plus one other. Each choir member is given the opportunity to rank each worship service available from most preferred to least, and these preferences are taken into consideration when creating the groups. Other considerations include:
-  If the choir member is an officer of a different department that would make them unavailable for one of the weekend services.
- Ensuring that each service contains half of each total number of choir members by voice. This is to make sure the choir is properly balanced by voice, with Soprano being the most prominent.
- Ensuring that each choir member is assigned 2 services, no more, no less.

This script outputs a CSV file for each special service, and this CSV file contains each choir member assigned to perform, with the headers being each voice.

This script also outputs a full master list of the choir in CSV format which lists their responses to each question in the Google Form plus their additional service (for leadership to assist with bookkeeping).

