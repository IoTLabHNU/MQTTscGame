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
