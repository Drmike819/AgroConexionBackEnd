CREATE DATABASE IF NOT EXISTS agroconexiondiagrama;
USE agroconexion;

-- Tipos de usuario
CREATE TABLE IF NOT EXISTS types (
    typeId INT AUTO_INCREMENT PRIMARY KEY,
    typeName VARCHAR(100) UNIQUE NOT NULL,
    typeDescription VARCHAR(200) UNIQUE NOT NULL
);

-- Métodos de pago
CREATE TABLE IF NOT EXISTS methods_of_payment (
    paymentId INT AUTO_INCREMENT PRIMARY KEY,
    paymentName VARCHAR(20) NOT NULL
);

-- Estados generales (para productos, facturas, etc.)
CREATE TABLE IF NOT EXISTS all_status (
    statusId INT AUTO_INCREMENT PRIMARY KEY,
    statusName VARCHAR(20) NOT NULL UNIQUE,
    statusDescription VARCHAR(200) NOT NULL
);

-- Usuarios
CREATE TABLE IF NOT EXISTS users (
    userId INT AUTO_INCREMENT PRIMARY KEY,
    userName VARCHAR(20) UNIQUE NOT NULL,
    userEmail VARCHAR(100) UNIQUE NOT NULL,
    userPhone VARCHAR(13) UNIQUE NOT NULL,
    userAddress VARCHAR(200) NOT NULL,
    userImage VARCHAR(255) NOT NULL,
    userPassword VARCHAR(255) NOT NULL,
    userTypeId INT NOT NULL,
    CONSTRAINT FK_UserType FOREIGN KEY (userTypeId) REFERENCES types(typeId)
);

-- Categorías de productos
CREATE TABLE IF NOT EXISTS categories (
    categoryId INT AUTO_INCREMENT PRIMARY KEY,
    categoryName VARCHAR(20) NOT NULL UNIQUE,
    categoryDescription VARCHAR(200) NOT NULL UNIQUE
);

-- Productos
CREATE TABLE IF NOT EXISTS products (
    productId INT AUTO_INCREMENT PRIMARY KEY,
    productUserId INT,  -- Puede ser NULL si el usuario es eliminado
    productCategoryId INT NOT NULL,
    productName VARCHAR(100) NOT NULL,
    productDescription VARCHAR(200) NOT NULL,
    productPrice DECIMAL(10, 2) NOT NULL,
    productStock INT NOT NULL,
    productUnitOfMeasure VARCHAR(50) NOT NULL,
    productStatusId INT NOT NULL,
    CONSTRAINT FK_ProductUser FOREIGN KEY (productUserId) REFERENCES users(userId)
        ON DELETE SET NULL,
    CONSTRAINT FK_ProductCategory FOREIGN KEY (productCategoryId) REFERENCES categories(categoryId)
        ON DELETE RESTRICT,
    CONSTRAINT FK_ProductStatus FOREIGN KEY (productStatusId) REFERENCES all_status(statusId)
        ON DELETE RESTRICT
);

-- Carritos de compra (uno por usuario)
CREATE TABLE IF NOT EXISTS shoppingCart (
    cartId INT AUTO_INCREMENT PRIMARY KEY,
    cartUserId INT NOT NULL UNIQUE,
    CONSTRAINT FK_ShoppingCart_User FOREIGN KEY (cartUserId) REFERENCES users(userId)
);

-- Productos dentro del carrito
CREATE TABLE IF NOT EXISTS cart_products (
    cartId INT NOT NULL,
    productId INT NOT NULL,
    quantity INT DEFAULT 1,
    PRIMARY KEY(cartId, productId),
    CONSTRAINT FK_CartProducts_Cart FOREIGN KEY (cartId) REFERENCES shoppingCart(cartId)
        ON DELETE CASCADE,
    CONSTRAINT FK_CartProducts_Product FOREIGN KEY (productId) REFERENCES products(productId)
        ON DELETE CASCADE
);

-- Tabla de favoritos (uno por usuario)
CREATE TABLE IF NOT EXISTS favorites (
    favoriteId INT AUTO_INCREMENT PRIMARY KEY,
    favoriteUserId INT NOT NULL UNIQUE,
    CONSTRAINT FK_Favorites_User FOREIGN KEY (favoriteUserId) REFERENCES users(userId)
);

-- Productos favoritos por usuario
CREATE TABLE IF NOT EXISTS favorites_products (
    favoritesId INT NOT NULL,
    productId INT NOT NULL,
    PRIMARY KEY(favoritesId, productId),
    CONSTRAINT FK_FavoriteProduct_Favorites FOREIGN KEY (favoritesId) REFERENCES favorites(favoriteId)
        ON DELETE CASCADE,
    CONSTRAINT FK_FavoriteProduct_Product FOREIGN KEY (productId) REFERENCES products(productId)
        ON DELETE CASCADE
);

-- Facturas
CREATE TABLE IF NOT EXISTS invoices (
    invoicesId INT AUTO_INCREMENT PRIMARY KEY,
    invoicesUserId INT NOT NULL,
    invoicesAmount DECIMAL(10, 2) NOT NULL,
    invoicesIssue_date DATE NOT NULL,
    invoicesPaymentId INT NOT NULL,
    invoicesStatusId INT NOT NULL,
    CONSTRAINT FK_Invoices_User FOREIGN KEY (invoicesUserId) REFERENCES users(userId)
        ON DELETE CASCADE,
    CONSTRAINT FK_Invoices_Payment FOREIGN KEY (invoicesPaymentId) REFERENCES methods_of_payment(paymentId),
    CONSTRAINT FK_Invoices_Status FOREIGN KEY (invoicesStatusId) REFERENCES all_status(statusId)
);

-- Detalles de cada factura
CREATE TABLE IF NOT EXISTS details_of_invoice (
    datInvId INT AUTO_INCREMENT PRIMARY KEY,
    datInvInvoicesId INT NOT NULL,
    datInvProductId INT NOT NULL,
    datInvProductUserId INT, -- Puede ser NULL si el vendedor fue eliminado
    datInvQuantity INT NOT NULL,
    datInvUnitPrice DECIMAL(10, 2) NOT NULL,
    CONSTRAINT FK_DetailInvoice_Invoice FOREIGN KEY (datInvInvoicesId) REFERENCES invoices(invoicesId)
        ON DELETE CASCADE,
    CONSTRAINT FK_DetailInvoice_Product FOREIGN KEY (datInvProductId) REFERENCES products(productId)
        ON DELETE RESTRICT,
    CONSTRAINT FK_DetailInvoice_User FOREIGN KEY (datInvProductUserId) REFERENCES users(userId)
        ON DELETE SET NULL
);
