CREATE DATABASE `ecn`;
USE `ecn`;
CREATE TABLE `client` (
    `code` VARCHAR(6) PRIMARY KEY,
    `first_name` VARCHAR(30),
    `last_name` VARCHAR(40),
    `company` VARCHAR(100),
    `vat` VARCHAR(10),
    `phone` VARCHAR(10),
    `cell` VARCHAR(10),
    `email` VARCHAR(50),
    `postal_address` VARCHAR(100),
    `physical_address` VARCHAR(100),
    `debit_order` BIT
);
CREATE TABLE `supplier` (
    `code` VARCHAR(6) PRIMARY KEY,
    `first_name` VARCHAR(30),
    `last_name` VARCHAR(40),
    `company` VARCHAR(100),
    `vat` VARCHAR(10),
    `phone` VARCHAR(10),
    `cell` VARCHAR(10),
    `email` VARCHAR(50),
    `postal_address` VARCHAR(100),
    `physical_address` VARCHAR(100)
);
CREATE TABLE `service` (
    `code` VARCHAR(6) PRIMARY KEY,
    `description` VARCHAR(100),
    `sales_price` NUMERIC(12,3),
    `cost_price` NUMERIC(12,3),
    `VAT` BIT,
    `supplier` VARCHAR(6),
    FOREIGN KEY (`supplier`) REFERENCES `supplier`(`code`)
);
CREATE TABLE `subscription` (
    `code` INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `client` VARCHAR(6),
    `service` VARCHAR(6),
    FOREIGN KEY (`client`) REFERENCES `client`(`code`),
    FOREIGN KEY (`service`) REFERENCES `service`(`code`)
);
CREATE TABLE `sales_invoice` (
	`code` INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `number` VARCHAR(6),
    `date` DATE,
    `client` VARCHAR(6),
    `service` VARCHAR(6),
    FOREIGN KEY (`client`) REFERENCES `client`(`code`),
    FOREIGN KEY (`service`) REFERENCES `service`(`code`)
);
CREATE TABLE `supplier_invoice` (
	`code` INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `number` VARCHAR(6),
    `date` DATE,
    `supplier` VARCHAR(6),
    `service` VARCHAR(6),
    FOREIGN KEY (`supplier`) REFERENCES `supplier`(`code`),
    FOREIGN KEY (`service`) REFERENCES `service`(`code`)
);
