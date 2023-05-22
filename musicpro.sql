-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 22-05-2023 a las 01:18:47
-- Versión del servidor: 10.4.28-MariaDB
-- Versión de PHP: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `musicpro`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `clientes`
--

CREATE TABLE `clientes` (
  `rut` varchar(10) NOT NULL,
  `nombre` varchar(100) DEFAULT NULL,
  `direccion` varchar(100) DEFAULT NULL,
  `telefono` varchar(15) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `clientes`
--

INSERT INTO `clientes` (`rut`, `nombre`, `direccion`, `telefono`) VALUES
('12345678-9', 'Robot', 'Robolandia', '12121212'),
('19385217-2', 'Nicol', 'Anibal Pinto 2570', '93023506'),
('20216817-5', 'Felipe Vega', 'Paicavi 834', '93023506');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pedidos`
--

CREATE TABLE `pedidos` (
  `id` int(11) NOT NULL,
  `rut_cliente` varchar(10) DEFAULT NULL,
  `fecha_pedido` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `pedidos`
--

INSERT INTO `pedidos` (`id`, `rut_cliente`, `fecha_pedido`) VALUES
(10, '12345678-9', '2023-05-01'),
(11, '19385217-2', '2023-03-10'),
(13, '12345678-9', '2023-05-10'),
(14, '12345678-9', '2023-05-04'),
(15, '12345678-9', '2023-05-04'),
(16, '12345678-9', '2023-05-04'),
(17, '20216817-5', '2023-03-31'),
(18, '20216817-5', '2023-05-10');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pedido_productos`
--

CREATE TABLE `pedido_productos` (
  `pedido_id` int(11) DEFAULT NULL,
  `producto_id` int(11) DEFAULT NULL,
  `cantidad` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `pedido_productos`
--

INSERT INTO `pedido_productos` (`pedido_id`, `producto_id`, `cantidad`) VALUES
(10, 2, 10),
(10, 3, 6),
(11, 7, 1),
(14, 10, 2),
(14, 9, 1),
(15, 10, 2),
(15, 9, 1),
(16, 10, 2),
(16, 9, 1),
(17, 4, 2),
(17, 6, 1),
(18, 4, 5),
(18, 2, 5);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `producto`
--

CREATE TABLE `producto` (
  `id` int(11) NOT NULL,
  `nombre` varchar(20) NOT NULL,
  `descripcion` varchar(100) NOT NULL,
  `categoria` varchar(20) NOT NULL,
  `precio` int(11) NOT NULL,
  `stock` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `producto`
--

INSERT INTO `producto` (`id`, `nombre`, `descripcion`, `categoria`, `precio`, `stock`) VALUES
(2, 'Guitarra Electrica X', 'La guitarra más cara que quiere tu hijo', 'Instrumentos', 299999, 5),
(3, 'Guitarra', 'Instrento de cuerdas', 'Instrumentos', 69000, 25),
(4, 'Bateria', 'Instrumento de tambor', 'Instrumentos', 129000, 113),
(6, 'Kalimba', 'Instrumento tipo minecraft', 'Instrumentos', 16000, 26),
(7, 'Microfono N-351', 'Pa cantar', 'Instrumentos', 32150, 61),
(9, 'Parlante x503', 'Reproduce sonidos wow', 'Parlantes', 99800, 2),
(10, 'Armonica Yamaha H2O', 'Instrumento de viento, se suele tocar en la cárcel', 'Instrumentos', 11990, 30),
(11, 'Audifonos 318K', 'pA ESCUCHAR MUSICA XD', 'Audifonos', 9990, 50),
(14, 'Violín', 'Cuerda que suena cuando la tocas con otra cuerda', 'Instrumentos', 29999, 0);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `clientes`
--
ALTER TABLE `clientes`
  ADD PRIMARY KEY (`rut`);

--
-- Indices de la tabla `pedidos`
--
ALTER TABLE `pedidos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `rut_cliente` (`rut_cliente`);

--
-- Indices de la tabla `pedido_productos`
--
ALTER TABLE `pedido_productos`
  ADD KEY `pedido_id` (`pedido_id`),
  ADD KEY `producto_id` (`producto_id`);

--
-- Indices de la tabla `producto`
--
ALTER TABLE `producto`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `pedidos`
--
ALTER TABLE `pedidos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT de la tabla `producto`
--
ALTER TABLE `producto`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `pedidos`
--
ALTER TABLE `pedidos`
  ADD CONSTRAINT `pedidos_ibfk_2` FOREIGN KEY (`rut_cliente`) REFERENCES `clientes` (`rut`);

--
-- Filtros para la tabla `pedido_productos`
--
ALTER TABLE `pedido_productos`
  ADD CONSTRAINT `pedido_productos_ibfk_1` FOREIGN KEY (`pedido_id`) REFERENCES `pedidos` (`id`),
  ADD CONSTRAINT `pedido_productos_ibfk_2` FOREIGN KEY (`producto_id`) REFERENCES `producto` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
