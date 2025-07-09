-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: mydb17
-- ------------------------------------------------------
-- Server version	5.5.5-10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `metal_prices`
--

DROP TABLE IF EXISTS `metal_prices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `metal_prices` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date DEFAULT NULL,
  `metal` varchar(255) DEFAULT NULL,
  `price_usd` float DEFAULT NULL,
  `unit` varchar(255) DEFAULT NULL,
  `price_php` float DEFAULT NULL,
  `pricephp_per_mg` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `metal_prices`
--

LOCK TABLES `metal_prices` WRITE;
/*!40000 ALTER TABLE `metal_prices` DISABLE KEYS */;
INSERT INTO `metal_prices` VALUES (1,'0000-00-00','gold',3084.4,'â‚±PESO/oz.',175773,6.2002),(2,'0000-00-00','silver',30.9,'â‚±PESO/oz.',1760.92,0.0621147),(3,'0000-00-00','copper',8539,'â‚±PESO/mt',486617,0.00048662),(4,'0000-00-00','aluminum',2285,'â‚±PESO/Tonne',130217,0.00013022),(5,'0000-00-00','lead',1820,'â‚±PESO/mt',103717,0.00010372),(6,'0000-00-00','nickel',13815,'â‚±PESO/mt',787284,0.00078728),(7,'0000-00-00','tin',29625,'â‚±PESO/mt',1688260,0.00168826),(8,'0000-00-00','zinc',2534,'â‚±PESO/mt',144407,0.00014441),(9,'0000-00-00','platinum',923.9,'â‚±PESO/troyOz.',52650.9,1.69276),(10,'0000-00-00','palladium',892,'â‚±PESO/troyOz.',50832.9,1.63432),(11,'0000-00-00','chromium',5.6,'â‚±PESO/lb.',319.13,0.00070356),(12,'0000-00-00','iron',713,'â‚±PESO/mt',40632.2,0.00004063);
/*!40000 ALTER TABLE `metal_prices` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-04-28  8:17:19
