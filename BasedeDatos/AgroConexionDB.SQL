CREATE DATABASE IF NOT EXISTS agroconexion;
USE agroconexion;

CREATE TABLE IF NOT EXISTS types (
    typeId INT AUTO_INCREMENT,
    typeName VARCHAR(100) UNIQUE NOT NULL,
    typeDescription VARCHAR(200) UNIQUE NOT NULL,
    PRIMARY KEY(typeId)
);

CREATE TABLE IF NOT EXISTS methods_of_payment (
    paymentId INT AUTO_INCREMENT,
    paymentName VARCHAR(20) NOT NULL,
    PRIMARY KEY(paymentId)
);

CREATE TABLE IF NOT EXISTS all_status (
    statusId INT AUTO_INCREMENT,
    statusName VARCHAR(20) NOT NULL UNIQUE,
    statusDescription VARCHAR(200) NOT NULL,
    PRIMARY KEY(statusId)
);

CREATE TABLE IF NOT EXISTS users (
    userId INT AUTO_INCREMENT,
    userName VARCHAR(20) UNIQUE NOT NULL,
    userEmail VARCHAR(100) UNIQUE NOT NULL,
    userPhone VARCHAR(13) UNIQUE NOT NULL,
    userAddress VARCHAR(200) NOT NULL,
    userImage VARCHAR(255) NOT NULL,
    userPassword VARCHAR(255) NOT NULL,
    userTypeId INT NOT NULL,
    PRIMARY KEY(userId),
    CONSTRAINT FK_UserType FOREIGN KEY (userTypeId) REFERENCES types(typeId)
);

CREATE TABLE IF NOT EXISTS categories (
    categoryId INT AUTO_INCREMENT,
    categoryName VARCHAR(20) NOT NULL UNIQUE,
    categoryDescription VARCHAR(200) NOT NULL UNIQUE,
    PRIMARY KEY(categoryId)
);

CREATE TABLE IF NOT EXISTS products (
    productId INT AUTO_INCREMENT,
    productUserId INT NOT NULL,
    productCategoryId INT NOT NULL,
    productName VARCHAR(100) NOT NULL,
    productDescription VARCHAR(200) NOT NULL,
    productPrice DECIMAL(10, 2) NOT NULL,
    productStock INT NOT NULL,
    productUnitOfMeasure VARCHAR(50) NOT NULL,
    productStatusId INT NOT NULL,
    PRIMARY KEY(productId),
    CONSTRAINT FK_ProductCategory FOREIGN KEY (productCategoryId) REFERENCES categories(categoryId),
    CONSTRAINT FK_ProductUser FOREIGN KEY (productUserId) REFERENCES users(userId),
    CONSTRAINT FK_ProductStatus FOREIGN KEY (productStatusId) REFERENCES all_status(statusId)
);

CREATE TABLE IF NOT EXISTS shoppingCart (
    cartId INT AUTO_INCREMENT,
    cartUserId INT NOT NULL UNIQUE,
    PRIMARY KEY(cartId),
    CONSTRAINT FK_ShoppingCart_User FOREIGN KEY (cartUserId) REFERENCES users(userId)
);

CREATE TABLE IF NOT EXISTS cart_products (
    cartId INT NOT NULL,
    productId INT NOT NULL,
    quantity INT DEFAULT 1,
    PRIMARY KEY(cartId, productId),
    CONSTRAINT FK_CartProducts_Cart FOREIGN KEY (cartId) REFERENCES shoppingCart(cartId),
    CONSTRAINT FK_CartProducts_Product FOREIGN KEY (productId) REFERENCES products(productId)
);

CREATE TABLE IF NOT EXISTS favorites (
    favoriteId INT AUTO_INCREMENT,
    favoriteUserId INT NOT NULL UNIQUE,
    PRIMARY KEY(favoriteId),
    CONSTRAINT FK_Favorites_User FOREIGN KEY (favoriteUserId) REFERENCES users(userId)
);

CREATE TABLE IF NOT EXISTS favorites_products (
    favoritesId INT NOT NULL,
    productId INT NOT NULL,
    PRIMARY KEY(favoritesId, productId),
    CONSTRAINT FK_FavoriteProduct_Product FOREIGN KEY (productId) REFERENCES products(productId),
    CONSTRAINT FK_FavoriteProduct_Favorites FOREIGN KEY (favoritesId) REFERENCES favorites(favoriteId)
);

CREATE TABLE IF NOT EXISTS invoices (
    invoicesId INT AUTO_INCREMENT,
    invoicesUserId INT NOT NULL,
    invoicesAmount DECIMAL(10, 2) NOT NULL,
    invoicesIssue_date DATE NOT NULL,
    invoicesPaymentId INT NOT NULL,
    invoicesStatusId INT NOT NULL,
    PRIMARY KEY(invoicesId),
    CONSTRAINT FK_Invoices_User FOREIGN KEY (invoicesUserId) REFERENCES users(userId),
    CONSTRAINT FK_Invoices_Payment FOREIGN KEY (invoicesPaymentId) REFERENCES methods_of_payment(paymentId),
    CONSTRAINT FK_Invoices_Status FOREIGN KEY (invoicesStatusId) REFERENCES all_status(statusId)
);

CREATE TABLE IF NOT EXISTS details_of_invoice (
    datInvId INT AUTO_INCREMENT,
    datInvInvoicesId INT NOT NULL,
    datInvProductId INT NOT NULL,
    datInvProductUserId INT NOT NULL,
    datInvQuantity INT NOT NULL,
    datInvUnitPrice DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY(datInvId),
    CONSTRAINT FK_DetailInvoice_Invoice FOREIGN KEY (datInvInvoicesId) REFERENCES invoices(invoicesId),
    CONSTRAINT FK_DetailInvoice_Product FOREIGN KEY (datInvProductId) REFERENCES products(productId),
    CONSTRAINT FK_DetailInvoice_User FOREIGN KEY (datInvProductUserId) REFERENCES users(userId)
);
