SELECT * FROM ecn.subscription;

# Total Monthly Sales
SELECT SUM(sales_price) FROM ecn.subscription, ecn.service where ecn.subscription.service = ecn.service.code;

# Total Monthly Pruchases
SELECT SUM(cost_price) FROM ecn.subscription, ecn.service where ecn.subscription.service = ecn.service.code;

# Join Clients, subscriptions and services
SELECT 
	first_name, 
    last_name, 
    company,
    service.description,
    cost_price,
    sales_price
FROM ecn.client, ecn.subscription, ecn.service 
where ecn.client.code = ecn.subscription.client 
and ecn.subscription.service = ecn.service.code
ORDER BY company, last_name, first_name;

# Debit order report
SELECT 
	ecn.client.code,
    ecn.client.first_name, 
	ecn.client.last_name, 
    ecn.client.company,
    SUM(ecn.service.sales_price)
FROM ecn.client, ecn.subscription, ecn.service 
WHERE ecn.client.code = ecn.subscription.client 
AND ecn.subscription.service = ecn.service.code
GROUP BY ecn.client.code;

# Recon
SELECT 
	supplier.company AS 'Supplier',
	service.description AS 'Description',
    COUNT(service.code) AS '#',
    SUM(sales_price) AS 'Monthly Sales', 
    SUM(cost_price) AS 'Monthly Purchases',
    SUM(sales_price) - SUM(cost_price) AS 'Monthly Profit'
FROM ecn.subscription, ecn.service, ecn.supplier 
where ecn.subscription.service = ecn.service.code
AND ecn.supplier.code = ecn.service.supplier
AND ecn.supplier.code = 'is0001'
GROUP BY service.code; 

# Domain renewals
SELECT
	client.first_name,
    client.last_name,
    client.company,
    service.description,
    subscription.description,
    service.cost_price*12
FROM client, subscription, service
WHERE subscription.client = client.code
AND subscription.service = service.code
AND service.type = 'domain';

# IS Uncapped and Per GB DSL
SELECT
	client.first_name,
    client.last_name,
    client.company,
    service.description,
    service.cost_price
FROM client, subscription, service
WHERE subscription.client = client.code
AND subscription.service = service.code
AND service.supplier = 'is0001'
AND service.type = 'uncapped';