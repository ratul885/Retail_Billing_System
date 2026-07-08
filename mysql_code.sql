create database final_project_retail_jan_2026;
use final_project_retail_jan_2026;
create table cust_details(
cust_id int auto_increment primary key,
cust_full_name varchar(255) not null,
cust_address varchar(500) not null,
cust_ph_number bigint not null
);
select * from cust_details;
insert into cust_details(cust_full_name, cust_address, cust_ph_number) values("Rajdeep","Kolkata",7869877894);
CREATE TABLE product_details (
    p_id INT PRIMARY KEY AUTO_INCREMENT,
    p_name VARCHAR(255) NOT NULL,
    p_price DECIMAL(10,2) NOT NULL,
    stock_in_hand INT NOT NULL
);

select * from product_details;
INSERT INTO product_details (p_name,p_price,stock_in_hand) VALUES
('Rice 5kg', 320.00, 50),
('Wheat Flour 5kg', 245.00, 45),
('Mustard Oil 1L', 185.00, 60),
('Sunflower Oil 1L', 165.00, 55),
('Sugar 1kg', 48.00, 80),
('Salt 1kg', 25.00, 100),
('Toor Dal 1kg', 145.00, 40),
('Masoor Dal 1kg', 118.00, 50),
('Moong Dal 1kg', 135.00, 45),
('Chana Dal 1kg', 92.00, 60),

('Basmati Rice 1kg', 120.00, 35),
('Tea Powder 500g', 210.00, 30),
('Coffee Powder 200g', 275.00, 25),
('Milk 1L', 64.00, 70),
('Bread Large', 45.00, 40),
('Butter 500g', 285.00, 25),
('Cheese Slices 200g', 140.00, 30),
('Eggs 12 pcs', 84.00, 90),
('Curd 500g', 40.00, 45),
('Paneer 200g', 90.00, 30),

('Maggi Noodles Pack', 15.00, 100),
('Biscuit Pack', 30.00, 75),
('Corn Flakes 500g', 185.00, 20),
('Tomato Ketchup 500g', 110.00, 25),
('Peanut Butter 500g', 240.00, 20),
('Jam Mixed Fruit 500g', 130.00, 25),
('Turmeric Powder 200g', 48.00, 35),
('Red Chilli Powder 200g', 70.00, 35),
('Cumin Powder 100g', 58.00, 30),
('Garam Masala 100g', 85.00, 25),

('Potato 1kg', 32.00, 120),
('Onion 1kg', 38.00, 110),
('Tomato 1kg', 45.00, 90),
('Apple 1kg', 180.00, 35),
('Banana Dozen', 70.00, 40),
('Orange 1kg', 95.00, 40),
('Mineral Water 1L', 20.00, 100),
('Soft Drink 750ml', 45.00, 60),
('Detergent Powder 1kg', 115.00, 50),
('Bath Soap Pack of 4', 145.00, 35);
select * from cust_details;
select * from product_details;
CREATE TABLE audit_table (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    total_bill_amount DECIMAL(10,2) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
select * from cust_details;
select * from product_details;
select * from audit_table;
DELETE FROM cust_details
WHERE cust_id = 3;
CREATE TABLE BILL_DETAILS_TABLE (
    SLNO INT PRIMARY KEY AUTO_INCREMENT,
    BILL_ID INT NOT NULL,
    C_ID INT NOT NULL,
    C_NAME VARCHAR(250) NOT NULL,
    P_ID INT NOT NULL,
    P_NAME VARCHAR(250) NOT NULL,
    P_PRICE DECIMAL(10,2) NOT NULL,
    p_quantity int not null,
    TIMESTAMP DATETIME DEFAULT CURRENT_TIMESTAMP
);
select * from cust_details;
select * from product_details;
select * from audit_table;
select * from BILL_DETAILS_TABLE;

select P_ID,P_NAME,sum(p_PRICE*p_quantity) as Total_Sales_amount
from BILL_DETAILS_TABLE group by P_ID,P_NAME order by Total_Sales_Amount DESC limit 5;




































 

