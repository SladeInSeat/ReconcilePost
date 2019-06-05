# ReconcilePost

Designed to run on GIS-cluster on a weekly schedule, this script automates the reconcile and post workflow for designated databases. Explicitly ignores designated actively used development databases.
Logs of the reconcile and post process are parsed with reg ex to identify failed attempts or errors, which are condensed and emailed to GIS support staff.
