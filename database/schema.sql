-- Mostrar este archivo completo en el editor.
-- Destacar las claves foráneas y la tabla stock como nexo
-- entre productos y sucursales.

USE chilepal_db;

CREATE TABLE IF NOT EXISTS sucursales (
    id_sucursal    INT AUTO_INCREMENT PRIMARY KEY,
    ciudad         VARCHAR(100) NOT NULL,
    direccion      VARCHAR(200) NOT NULL,
    telefono       VARCHAR(20),
    activa         BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario     INT AUTO_INCREMENT PRIMARY KEY,
    nombre         VARCHAR(100) NOT NULL,
    email          VARCHAR(100) UNIQUE NOT NULL,
    password       VARCHAR(255) NOT NULL,
    rol            ENUM('admin','vendedor','frigorifico','repartidor','cliente') NOT NULL,
    id_sucursal    INT,
    activo         BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_sucursal) REFERENCES sucursales(id_sucursal)
);

CREATE TABLE IF NOT EXISTS productos (
    id_producto    INT AUTO_INCREMENT PRIMARY KEY,
    nombre         VARCHAR(100) NOT NULL,
    variedad       VARCHAR(50)  NOT NULL,
    calibre        ENUM('extra','primera','segunda','tercera','descarte'),
    precio_kg      DECIMAL(10,2) NOT NULL,
    es_temporada   BOOLEAN DEFAULT FALSE,
    activo         BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS stock (
    id_stock             INT AUTO_INCREMENT PRIMARY KEY,
    id_producto          INT NOT NULL,
    id_sucursal          INT NOT NULL,
    cantidad_kg          DECIMAL(10,2) NOT NULL DEFAULT 0,
    fecha_actualizacion  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    FOREIGN KEY (id_sucursal) REFERENCES sucursales(id_sucursal),
    UNIQUE KEY uq_prod_suc (id_producto, id_sucursal)
);

CREATE TABLE IF NOT EXISTS pedidos (
    id_pedido      INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente     INT NOT NULL,
    id_vendedor    INT NOT NULL,
    id_sucursal    INT NOT NULL,
    fecha_pedido   DATETIME DEFAULT CURRENT_TIMESTAMP,
    estado         ENUM('pendiente','confirmado','en_preparacion','despachado','entregado','cancelado') DEFAULT 'pendiente',
    total          DECIMAL(10,2) DEFAULT 0,
    observaciones  TEXT,
    FOREIGN KEY (id_cliente)  REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_vendedor) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_sucursal) REFERENCES sucursales(id_sucursal)
);

CREATE TABLE IF NOT EXISTS detalle_pedido (
    id_detalle       INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido        INT NOT NULL,
    id_producto      INT NOT NULL,
    cantidad_kg      DECIMAL(10,2) NOT NULL,
    precio_unitario  DECIMAL(10,2) NOT NULL,
    subtotal         DECIMAL(10,2) GENERATED ALWAYS AS (cantidad_kg * precio_unitario) STORED,
    FOREIGN KEY (id_pedido)   REFERENCES pedidos(id_pedido),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

CREATE TABLE IF NOT EXISTS despachos (
    id_despacho       INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido         INT NOT NULL UNIQUE,
    id_repartidor     INT NOT NULL,
    fecha_despacho    DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_entrega     DATETIME,
    estado            ENUM('en_preparacion','en_camino','entregado') DEFAULT 'en_preparacion',
    direccion_destino VARCHAR(200),
    FOREIGN KEY (id_pedido)     REFERENCES pedidos(id_pedido),
    FOREIGN KEY (id_repartidor) REFERENCES usuarios(id_usuario)
);

CREATE TABLE IF NOT EXISTS pagos (
    id_pago             INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido           INT NOT NULL UNIQUE,
    monto               DECIMAL(10,2) NOT NULL,
    fecha_pago          DATETIME DEFAULT CURRENT_TIMESTAMP,
    metodo              ENUM('efectivo','transferencia','cheque') NOT NULL,
    numero_comprobante  VARCHAR(100) UNIQUE,
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido)
);

-- ── Datos iniciales ───────────────────────────────────────────

INSERT IGNORE INTO sucursales (id_sucursal, ciudad, direccion, telefono) VALUES
(1, 'Quillota', 'Av. Los Carrera 1240, Quillota', '+56 33 2123456'),
(2, 'Chillán',  'Calle Arauco 890, Chillán',       '+56 42 2234567');

INSERT IGNORE INTO productos (id_producto, nombre, variedad, calibre, precio_kg, es_temporada) VALUES
(1, 'Palta Hass Extra',    'hass',    'extra',    3200.00, FALSE),
(2, 'Palta Hass Primera',  'hass',    'primera',  2800.00, FALSE),
(3, 'Palta Hass Segunda',  'hass',    'segunda',  2200.00, FALSE),
(4, 'Palta Hass Tercera',  'hass',    'tercera',  1600.00, FALSE),
(5, 'Palta Hass Descarte', 'hass',    'descarte',  900.00, FALSE),
(6, 'Mango Kent',          'mango',    NULL,       2500.00, TRUE),
(7, 'Naranja Valencia',    'naranja',  NULL,        850.00, TRUE),
(8, 'Limón Eureka',        'limon',    NULL,        780.00, TRUE);

INSERT IGNORE INTO stock (id_producto, id_sucursal, cantidad_kg) VALUES
(1,1,500),(2,1,1200),(3,1,800),(4,1,600),(5,1,300),(6,1,150),(7,1,400),(8,1,300),
(1,2,350),(2,2,900), (3,2,600),(4,2,400),(5,2,200),(6,2,100),(7,2,250),(8,2,200);
