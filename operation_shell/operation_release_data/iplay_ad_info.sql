-- MySQL dump 10.13  Distrib 5.5.41, for debian-linux-gnu (x86_64)
--
-- Host: 106.187.54.178    Database: forum
-- ------------------------------------------------------
-- Server version	5.5.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `iplay_ad_info`
--

DROP TABLE IF EXISTS `iplay_ad_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `iplay_ad_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` int(11) NOT NULL COMMENT '使用场景: type=1,用于游戏安装时的等待页面',
  `package_name` varchar(512) DEFAULT NULL COMMENT '游戏id, 可以为空, 表明该位置的缺省广告, 否则是对应某游戏的广告',
  `order_num` int(11) DEFAULT '0' COMMENT '在当前type和game_id下的顺序, 最终返回给客户端时会按照此顺序排序, 缺省广告会排在game_id专有广告之后一起返回',
  `title` varchar(1000) DEFAULT NULL COMMENT '只有在通知栏位置显示广告时需要填写标题',
  `content` text COMMENT '广告内容',
  `pic_url` varchar(1000) DEFAULT NULL COMMENT '广告图片地址',
  `big_pic_url` varchar(1000) DEFAULT NULL COMMENT '目前只用于通知栏大图标 (+)',
  `target_type` int(11) DEFAULT NULL COMMENT '点击后的跳转目标类型: 0=不可点击 1=网页地址 2=游戏详情页',
  `target` varchar(1000) DEFAULT NULL COMMENT '跳转目标: 网页地址 或 游戏的game_id',
  `pkg_name` varchar(1000) DEFAULT NULL COMMENT '广告目标的包名，用于在客户端滤重 (+)',
  `ver_name` varchar(45) DEFAULT NULL COMMENT '版本号 (+)',
  `size` int(11) DEFAULT NULL COMMENT '文件大小，单位byte (+)',
  `filename` varchar(1000) DEFAULT NULL COMMENT '应用文件名 (+)',
  `show_delay` int(11) DEFAULT NULL COMMENT '广告展示延时 (+)',
  `next_delay` int(11) DEFAULT NULL COMMENT '下次广告展示延时 (+)',
  `filter_pkg_names` varchar(1000) DEFAULT NULL COMMENT '广告目标的包名列表,用于在客户端滤重 (+)',
  `channels` varchar(128) NOT NULL COMMENT '渠道号 (+)',
  `life_time` int(11) DEFAULT '48' COMMENT '广告的生命期,单位h',
  `monet_silent` tinyint(4) DEFAULT '0' COMMENT '移动网络静默下载:0-不静默下载, 1-静默下载',
  `download_dismissible` tinyint(4) DEFAULT '0' COMMENT '广告下载通知栏是否可被划去(0/1) 0-不可被划去, 1-可被划去',
  `install_dismissible` tinyint(4) DEFAULT '0' COMMENT '广告安装通知栏是否可被划去(0/1) 0-不可被划去, 1-可被划去',
  `wifi_silent` tinyint(4) DEFAULT '1' COMMENT 'WIFI网络静默下载:0-不静默下载, 1-静默下载',
  `enable` tinyint(4) DEFAULT '1' COMMENT '广告是否有效:0-无效,1-有效',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=83 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `iplay_ad_info`
--

LOCK TABLES `iplay_ad_info` WRITE;
/*!40000 ALTER TABLE `iplay_ad_info` DISABLE KEYS */;
INSERT INTO `iplay_ad_info` VALUES (72,4,'default',6,'武媚娘传奇','同名正版唯一官方授权手游，以剧情同步、策略宫斗、皇权大战、华服盛宴。','http://img.wdjimg.com/mms/icon/v1/4/dd/d002bff246f42177d0463d327b289dd4_256_256.png','http://7mnn9f.com1.z0.glb.clouddn.com/wmncq.jpg',3,'http://api.np.mobilem.360.cn/redirect/down/?from=lm_101560&appid=2407335','com.atme.wuzetian.qihoo','1.4.0',99424132,'武媚娘传奇.apk',60,43200,'[\"\"]','A100',48,0,0,1,1,1),(68,4,'default',7,'崩坏学院2','满满的萌妹子让我等屌丝欲罢不能。','http://img.wdjimg.com/mms/icon/v1/8/09/f0e550e038a3e816bb3231db9fe22098_256_256.png','http://7mnn9f.com1.z0.glb.clouddn.com/bhxy2.jpg',3,'http://api.np.mobilem.360.cn/redirect/down/?from=lm_101560&appid=1712686','com.miHoYo.HSoDv22144.qihoo','2.0.17',261418343,'bengkuai.apk',30,43200,'[\"\"]','A100',48,0,1,1,0,1),(66,2,'default',1,'天天枪战','天天枪战游戏','http://7mnn9f.com1.z0.glb.clouddn.com/512.png','http://7mnn9f.com1.z0.glb.clouddn.com/480-800-1_%E5%89%AF%E6%9C%AC.jpg',3,'http://gdown.baidu.com/data/wisegame/259c2697306a0dad/F18feixingjian_24.apk','com.wyd.gunsoul.tq','1.3.0',89885225,'tiantianqiangzhan.apk',30,43200,'','A100',48,0,0,0,1,1),(67,2,'default',4,'刀塔传奇','dota游戏','http://img.wdjimg.com/mms/icon/v1/1/2f/651fa66fab7000f5f5717ad193a6b2f1_256_256.png','http://img.wdjimg.com/mms/screenshot/b/84/c3fb7f35bbf80d371f7fd33a3586884b_320_568.jpeg',3,'http://gdown.baidu.com/data/wisegame/d4a77a2019157aca/boyasichuanmajiang_40.apk','sh.lilith.dgame.s360','3.2.2',200216668,'dotachuan.apk',30,43200,'','A100',48,0,0,0,1,1),(74,4,'default',5,'召唤师联盟','召唤师联盟召唤师联盟','http://img.wdjimg.com/mms/icon/v1/4/26/844bc811870302eb153b48c73ca49264_256_256.png','http://7mnn9f.com1.z0.glb.clouddn.com/zhslm.jpg',3,'http://api.np.mobilem.360.cn/redirect/down/?from=lm_101560&appid=2794021','com.Longame.zhslm.qihu','1.3.01',128111112,'zhaohuanshi.apk',30,43200,'[\"\"]','A100',48,0,1,1,0,1),(75,4,'default',3,'无双剑姬','无双剑姬无双剑姬','http://p18.qhimg.com/t016c7ada52eeb86b1b.png ','http://7mnn9f.com1.z0.glb.clouddn.com/Z-(9).jpg',3,'http://api.np.mobilem.360.cn/redirect/down/?from=lm_101560&appid=1964946','com.kunlun.wsjj.qihoo','1.0.10',198288047,'wujianshuangji.apk',30,43200,'[\"com.microgames.deadninja\", \"com.mediocre.commute\"]','A100',48,0,1,0,0,1),(82,4,'default',2,'LBE安全大师','安卓平台最先进的手机权限管理工具。','http://cdn1.lbesec.com/icon/256.png','http://cdn1.lbesec.com/static/img/cpa/banner.A7.jpg',3,'http://aup.lbesec.com/r2?id=1505131','com.lbe.security','6.1.1504',8394887,'lbe.apk',120,43200,'[\"\"]','B2,A100',48,1,0,0,1,1);
/*!40000 ALTER TABLE `iplay_ad_info` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-05-22 15:36:37
