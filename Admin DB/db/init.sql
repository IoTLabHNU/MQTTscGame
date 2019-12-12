CREATE DATABASE admindb;
use admindb;
-- MySQL Script generated by MySQL Workbench
-- Tue Dec 10 11:22:50 2019
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema admindb
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema admindb
-- -----------------------------------------------------
USE `admindb` ;

-- -----------------------------------------------------
-- Table `admindb`.`game`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `admindb`.`game` (
  `game_id` VARCHAR(10) NOT NULL,
  `rounds` INT(11) NOT NULL,
  PRIMARY KEY (`game_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `admindb`.`tier`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `admindb`.`tier` (
  `tier_id` VARCHAR(10) NOT NULL,
  `company_name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`tier_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `admindb`.`products`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `admindb`.`products` (
  `product_id` VARCHAR(10) NOT NULL,
  `product_name` VARCHAR(45) NOT NULL,
  `type` VARCHAR(45) NOT NULL,
  `production_time` INT(11) NOT NULL,
  `cost` INT(11) NOT NULL,
  `prerequisites` VARCHAR(70) NOT NULL,
  `prerequisites_amounts` VARCHAR(45) NOT NULL,
  `tier_tier_id` VARCHAR(10) NOT NULL,
  `initial_amount` INT(10) NULL DEFAULT NULL,
  PRIMARY KEY (`product_id`),
  INDEX `fk_products_tier1_idx` (`tier_tier_id` ASC) ,
  CONSTRAINT `fk_products_tier1`
    FOREIGN KEY (`tier_tier_id`)
    REFERENCES `admindb`.`tier` (`tier_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `admindb`.`initialinventory`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `admindb`.`initialinventory` (
  `products_product_id` VARCHAR(10) NOT NULL,
  `amount` INT(11) NOT NULL,
  PRIMARY KEY (`products_product_id`),
  INDEX `fk_initialInventory_products1_idx` (`products_product_id` ASC) ,
  CONSTRAINT `fk_initialInventory_products1`
    FOREIGN KEY (`products_product_id`)
    REFERENCES `admindb`.`products` (`product_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `admindb`.`round`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `admindb`.`round` (
  `round_id` VARCHAR(10) NOT NULL,
  `round_number` INT(11) NOT NULL,
  `round_length` INT(11) NOT NULL,
  `start_time` DATETIME NOT NULL,
  `end_time` DATETIME NOT NULL,
  `game_id` VARCHAR(10) NOT NULL,
  PRIMARY KEY (`round_id`),
  INDEX `fk_Round_game1_idx` (`game_id` ASC) ,
  CONSTRAINT `fk_Round_game1`
    FOREIGN KEY (`game_id`)
    REFERENCES `admindb`.`game` (`game_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `admindb`.`type`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `admindb`.`type` (
  `type_id` VARCHAR(10) NOT NULL,
  `transaction_name` VARCHAR(45) NOT NULL,
  `description` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`type_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `admindb`.`transaction`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `admindb`.`transaction` (
  `transaction_id` VARCHAR(10) NOT NULL,
  `to_tier_id` VARCHAR(10) NOT NULL,
  `from_tier_id` VARCHAR(10) NOT NULL,
  `transaction_type_id` VARCHAR(10) NOT NULL,
  `amount` INT(11) NOT NULL,
  `product_id` VARCHAR(10) NOT NULL,
  `Round_round_id` VARCHAR(10) NOT NULL,
  `time_stamp` DATETIME NOT NULL,
  PRIMARY KEY (`transaction_id`),
  INDEX `fk_transactions_tier_idx` (`to_tier_id` ASC) ,
  INDEX `fk_transactions_tier1_idx` (`from_tier_id` ASC) ,
  INDEX `fk_transaction_transactions1_idx` (`transaction_type_id` ASC) ,
  INDEX `fk_transaction_Round1_idx` (`Round_round_id` ASC) ,
  INDEX `fk_transactions_products_idx` (`product_id` ASC) ,
  CONSTRAINT `fk_transaction_Round1`
    FOREIGN KEY (`Round_round_id`)
    REFERENCES `admindb`.`round` (`round_id`),
  CONSTRAINT `fk_transaction_transactions1`
    FOREIGN KEY (`transaction_type_id`)
    REFERENCES `admindb`.`type` (`type_id`),
  CONSTRAINT `fk_transactions_products`
    FOREIGN KEY (`product_id`)
    REFERENCES `admindb`.`products` (`product_id`),
  CONSTRAINT `fk_transactions_tier`
    FOREIGN KEY (`to_tier_id`)
    REFERENCES `admindb`.`tier` (`tier_id`),
  CONSTRAINT `fk_transactions_tier1`
    FOREIGN KEY (`from_tier_id`)
    REFERENCES `admindb`.`tier` (`tier_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

INSERT INTO `tier` (`tier_id`,`company_name`) VALUES ('1','AMK ');
INSERT INTO `tier` (`tier_id`,`company_name`) VALUES ('2','AMD');
INSERT INTO `tier` (`tier_id`,`company_name`) VALUES ('3','Intel');
INSERT INTO `tier` (`tier_id`,`company_name`) VALUES ('4','Ironside');
INSERT INTO `tier` (`tier_id`,`company_name`) VALUES ('5','OEM');

INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00001','Polyethylene','raw',0,100,'none','none','4',15);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00002','Iron','raw',0,100,'none','none','4',15);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00003','Diode','raw',0,100,'none','none','4',15);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00004','Rubber','raw',0,100,'none','none','4',15);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00005','Covers','fg',15,200,'Polyethylene#Iron#Diode#Rubber','1#0#0#0','4',10);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00006','Screw','fg',5,200,'Polyethylene#Iron#Diode#Rubber','0#1#0#0','4',10);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00007','LED','fg',10,300,'Polyethylene#Iron#Diode#Rubber','0#0#1#0','4',10);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00008','Grill','fg',15,400,'Polyethylene#Iron#Diode#Rubber','0#0#0#1','4',10);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00009','Covers','raw',0,200,'none','none','3',10);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00010','Screw','raw',0,200,'none','none','3',10);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00011','LED','raw',0,300,'none','none','3',10);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00012','Grill','raw',0,400,'none','none','3',10);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00013','Frames','fg',20,300,'Covers#Screw#LED#Grill','1#2#0#0','3',7);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00014','Fog lamp sockets','fg',5,300,'Covers#Screw#LED#Grill','0#1#1#0','3',7);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00015','Bubble','fg',10,400,'Covers#Screw#LED#Grill','0#0#1#0','3',7);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00016','Customized grill','fg',15,500,'Covers#Screw#LED#Grill','1#2#0#1','3',7);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00017','Frames','raw',0,300,'none','none','2',7);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00018','Fog lamp sockets','raw',0,300,'none','none','2',7);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00019','Bubble','raw',0,400,'none','none','2',7);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00020','Customized grill','raw',0,500,'none','none','2',7);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00021','Bumper','fg',20,350,'Frames#Fog lamp sockets#Bubble#Customized grill','2#2#2#1','2',5);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00022','Fog lamp','fg',5,350,'Frames#Fog lamp sockets#Bubble#Customized grill','0#1#1#0','2',5);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00023','LED Set','fg',10,450,'Frames#Fog lamp sockets#Bubble#Customized grill','0#0#1#0','2',5);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00024','Painted customized grill','fg',15,550,'Frames#Fog lamp sockets#Bubble#Customized grill','0#0#0#1','2',5);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00025','Bumper','raw',0,350,'none','none','1',5);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00026','Fog lamp','raw',0,350,'none','none','1',5);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00027','LED Set','raw',0,450,'none','none','1',5);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00028','Painted customized grill','raw',0,550,'none','none','1',5);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00029','Bumper BMW','fg',10,375,'Bumper#Fog lamp#LED Set#Painted customized grill','1#2#2#1','1',1);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00030','Bumper AUDI','fg',10,380,'Bumper#Fog lamp#LED Set#Painted customized grill','1#2#2#1','1',1);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00031','Bumper BENZ','fg',10,460,'Bumper#Fog lamp#LED Set#Painted customized grill','1#2#2#1','1',1);
INSERT INTO `products` (`product_id`,`product_name`,`type`,`production_time`,`cost`,`prerequisites`,`prerequisites_amounts`,`tier_tier_id`,`initial_amount`) VALUES ('prod00032','Bumper VW','fg',10,580,'Bumper#Fog lamp#LED Set#Painted customized grill','1#2#2#1','1',1);
