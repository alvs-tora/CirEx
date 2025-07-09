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
-- Table structure for table `metal_price_info`
--

DROP TABLE IF EXISTS `metal_price_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `metal_price_info` (
  `price_id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date DEFAULT NULL,
  `metal` varchar(50) DEFAULT NULL,
  `price_usd` decimal(10,2) DEFAULT NULL,
  `price_php` decimal(10,2) DEFAULT NULL,
  `default_unit` varchar(20) DEFAULT NULL,
  `price_php_per_mg` decimal(10,6) DEFAULT NULL,
  PRIMARY KEY (`price_id`),
  KEY `fk` (`date`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `metal_price_info`
--

LOCK TABLES `metal_price_info` WRITE;
/*!40000 ALTER TABLE `metal_price_info` DISABLE KEYS */;
INSERT INTO `metal_price_info` VALUES (1,'2025-04-09','gold',3084.40,175772.60,'PESO/oz.',6.200201),(2,'2025-04-09','silver',30.90,1760.92,'PESO/oz.',0.062115),(3,'2025-04-09','copper',8539.00,486617.24,'PESO/mt',0.000487),(4,'2025-04-09','aluminum',2285.00,130216.70,'PESO/Tonne',0.000130),(5,'2025-04-09','lead',1820.00,103717.46,'PESO/mt',0.000104),(6,'2025-04-09','nickel',13815.00,787283.90,'PESO/mt',0.000787),(7,'2025-04-09','tin',29625.00,1688258.09,'PESO/mt',0.001688),(8,'2025-04-09','zinc',2534.00,144406.62,'PESO/mt',0.000144),(9,'2025-04-09','platinum',923.90,52650.86,'PESO/troyOz.',1.692763),(10,'2025-04-09','palladium',892.00,50832.95,'PESO/troyOz.',1.634316),(11,'2025-04-09','chromium',5.60,319.13,'PESO/lb.',0.000704),(12,'2025-04-09','iron',713.00,40632.17,'PESO/mt',0.000041);
/*!40000 ALTER TABLE `metal_price_info` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-06 12:40:49
