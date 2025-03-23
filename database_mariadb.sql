CREATE DATABASE IF NOT EXISTS `social_media_pipeline` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `social_media_pipeline`;

-- Table structure for table `posts`
DROP TABLE IF EXISTS `posts`;
CREATE TABLE `posts` (
  `id` VARCHAR(100) NOT NULL,
  `platform` ENUM('x', 'facebook') NOT NULL DEFAULT 'x',
  `post_date` DATE NOT NULL,
  `post_time` TIME NOT NULL,
  `content` TEXT NOT NULL,
  `likes` INT(11) DEFAULT 0,
  `retweets` INT(11) DEFAULT 0,
  `comments` INT(11) DEFAULT 0,
  `scraped_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_platform` (`platform`),
  INDEX `idx_post_date` (`post_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table structure for table `top_comments`
DROP TABLE IF EXISTS `top_comments`;
CREATE TABLE `top_comments` (
  `post_id` VARCHAR(100) NOT NULL,
  `comments_count` INT(11) NOT NULL,
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`post_id`),
  CONSTRAINT `top_comments_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table structure for table `top_likes`
DROP TABLE IF EXISTS `top_likes`;
CREATE TABLE `top_likes` (
  `post_id` VARCHAR(100) NOT NULL,
  `likes_count` INT(11) NOT NULL,
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`post_id`),
  CONSTRAINT `top_likes_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table structure for table `top_retweets`
DROP TABLE IF EXISTS `top_retweets`;
CREATE TABLE `top_retweets` (
  `post_id` VARCHAR(100) NOT NULL,
  `retweets_count` INT(11) NOT NULL,
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`post_id`),
  CONSTRAINT `top_retweets_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table structure for table `word_frequency`
DROP TABLE IF EXISTS `word_frequency`;
CREATE TABLE `word_frequency` (
  `id` ENUM('x', 'facebook') NOT NULL DEFAULT 'x',
  `word` VARCHAR(100) NOT NULL,
  `count` INT(11) DEFAULT 1,
  PRIMARY KEY (`id`, `word`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table structure for table `hashtag_frequency`
DROP TABLE IF EXISTS `hashtag_frequency`;
CREATE TABLE `hashtag_frequency` (
  `id` enum('x','facebook') COLLATE utf8mb4_unicode_ci NOT NULL,
  `word` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `count` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`,`word`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;