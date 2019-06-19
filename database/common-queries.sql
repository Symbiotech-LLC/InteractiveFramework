/* Show Tables */
SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%Environments_%';

/* Example query to limit what to run script against */
Select * From 'Environments_AEM' Where Environment like 'dev' and Type Like 'author';
Select * From 'Environments_AEM' Where Type Like 'author';


/* Example query of AEM Node Creation */
select * From "Nodes_AEM" where scenario like 'tenant';
select * From "Nodes_AEM" where scenario like 'app';
select * From "Nodes_AEM" where scenario like 'locale';
select * From "Nodes_AEM" where scenario like 'no locale';
select * From "Nodes_AEM" where scenario like 'locale app';