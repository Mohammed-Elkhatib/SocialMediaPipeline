CREATE DATABASE  IF NOT EXISTS `social_media_pipeline` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `social_media_pipeline`;
-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: social_media_pipeline
-- ------------------------------------------------------
-- Server version	9.2.0

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
-- Table structure for table `engagement_metrics`
--

DROP TABLE IF EXISTS `engagement_metrics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `engagement_metrics` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `likes` int DEFAULT '0',
  `retweets` int DEFAULT '0',
  `comments` int DEFAULT '0',
  `platform_id` int NOT NULL,
  `post_id` bigint NOT NULL,
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `post_id` (`post_id`),
  KEY `platform_id` (`platform_id`),
  CONSTRAINT `engagement_metrics_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE,
  CONSTRAINT `engagement_metrics_ibfk_2` FOREIGN KEY (`platform_id`) REFERENCES `platforms` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `engagement_metrics`
--

LOCK TABLES `engagement_metrics` WRITE;
/*!40000 ALTER TABLE `engagement_metrics` DISABLE KEYS */;
INSERT INTO `engagement_metrics` VALUES (1,100,20,10,4,1,'2025-02-15 15:32:56'),(2,210,21,13,4,1,'2025-02-14 09:20:42'),(3,195,23,13,4,2,'2025-02-14 12:56:54'),(4,142,46,28,4,3,'2025-02-14 16:31:47'),(5,133,34,20,4,4,'2025-02-14 16:19:58'),(6,126,16,3,4,5,'2025-02-14 09:18:19');
/*!40000 ALTER TABLE `engagement_metrics` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `platforms`
--

DROP TABLE IF EXISTS `platforms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `platforms` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `platforms`
--

LOCK TABLES `platforms` WRITE;
/*!40000 ALTER TABLE `platforms` DISABLE KEYS */;
INSERT INTO `platforms` VALUES (4,'facebook'),(3,'pizza'),(5,'x');
/*!40000 ALTER TABLE `platforms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `posts`
--

DROP TABLE IF EXISTS `posts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `posts` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `platform_id` int NOT NULL,
  `post_date` date NOT NULL,
  `post_time` time NOT NULL,
  `content` text NOT NULL,
  `scraped_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `platform_id` (`platform_id`,`post_date`,`post_time`),
  CONSTRAINT `posts_ibfk_1` FOREIGN KEY (`platform_id`) REFERENCES `platforms` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `posts`
--

LOCK TABLES `posts` WRITE;
/*!40000 ALTER TABLE `posts` DISABLE KEYS */;
INSERT INTO `posts` VALUES (1,4,'2025-02-01','12:30:00','This is a sample post on Facebook!','2025-02-15 15:32:56'),(2,4,'2025-02-14','11:20:42','سعد الحريري: مسيرة رفيق الحريري مستمرة ومن حاول قتلها \"شوفوا وين صاروا\"','2025-02-14 09:20:42'),(3,4,'2025-02-14','14:56:54','الرئيس#سعد_الحريريبين جمهوره في#بيت_الوسط','2025-02-14 12:56:54'),(4,4,'2025-02-14','18:31:47','مصادر دبلوماسية لـ#الجديد: واشنطن أبلغت بعبدا عن تهديد إسرائيلي لمطار بيروت في حال استقبال الطائرة الإيرانية وجاء قرار المنع بموافقة السلطات اللبنانية الثلاثة حرصًا على أمن المطار@josephinedeeb','2025-02-14 16:31:47'),(5,4,'2025-02-14','18:19:58','معلومات#الجديد: تسيير رحلات جوية مباشرة بين بيروت وطهران قد يتوقف ليتم استبداله بالمرور في دولة أخرى قبل الوصول إلى طهران@josephinedeeb','2025-02-14 16:19:58'),(6,4,'2025-02-14','11:18:19','سعد الحريري يعلن عودة تيار المستقبل للعمل السياسي: هذا التيار باقٍ وسيكون صوتكم في كل الاستحقاقات والمحطات المقبلة','2025-02-14 09:18:19');
/*!40000 ALTER TABLE `posts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `top_comments`
--

DROP TABLE IF EXISTS `top_comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `top_comments` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `post_id` bigint NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `post_id` (`post_id`),
  CONSTRAINT `top_comments_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `top_comments`
--

LOCK TABLES `top_comments` WRITE;
/*!40000 ALTER TABLE `top_comments` DISABLE KEYS */;
INSERT INTO `top_comments` VALUES (1,1,'2025-02-14 11:35:55'),(2,2,'2025-02-14 11:35:55'),(3,3,'2025-02-14 16:31:47'),(4,4,'2025-02-14 16:31:47'),(5,5,'2025-02-14 16:19:58');
/*!40000 ALTER TABLE `top_comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `top_likes`
--

DROP TABLE IF EXISTS `top_likes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `top_likes` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `post_id` bigint NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `post_id` (`post_id`),
  CONSTRAINT `top_likes_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `top_likes`
--

LOCK TABLES `top_likes` WRITE;
/*!40000 ALTER TABLE `top_likes` DISABLE KEYS */;
INSERT INTO `top_likes` VALUES (1,1,'2025-02-14 09:20:42'),(2,2,'2025-02-14 12:56:54'),(3,3,'2025-02-14 16:31:47'),(4,4,'2025-02-14 16:19:58'),(5,5,'2025-02-14 09:18:19');
/*!40000 ALTER TABLE `top_likes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `word_frequency`
--

DROP TABLE IF EXISTS `word_frequency`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `word_frequency` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `word` varchar(100) DEFAULT NULL,
  `count` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `word_frequency`
--

LOCK TABLES `word_frequency` WRITE;
/*!40000 ALTER TABLE `word_frequency` DISABLE KEYS */;
INSERT INTO `word_frequency` VALUES (1,'الحريري',22),(2,'الجديد',19),(3,'الرئيس',13),(4,'سعد',13),(5,'للتفاصيل',8),(6,'المستقبل',7),(7,'السياسي',6),(8,'رفيق',5),(9,'josephinedeeb',5),(10,'رئيس',5),(11,'تيار',5),(12,'jacintheantar',4),(13,'اللبناني',4),(14,'يعلن',4),(15,'عودة',4),(16,'لبنان',3),(17,'الطائرة',3);
/*!40000 ALTER TABLE `word_frequency` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-03-13  7:23:22
