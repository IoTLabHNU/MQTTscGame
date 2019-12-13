CREATE DATABASE clientdb;
use clientdb;


SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';


-- -----------------------------------------------------
-- Schema clientdb
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Table `clientdb`.`tier`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `clientdb`.`tier` (
  `tier_id` INT(11) NOT NULL,
  `company_name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`tier_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `clientdb`.`product`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `clientdb`.`product` (
  `product_id` VARCHAR(10) NOT NULL,
  `product_name` VARCHAR(45) NOT NULL,
  `type` VARCHAR(45) NOT NULL,
  `production_time` INT(11) NOT NULL,
  `cost` DOUBLE NOT NULL,
  `prerequisites` VARCHAR(70) NOT NULL,
  `prerequisites_amount` VARCHAR(45) NOT NULL,
  `tier_id` INT(11) NOT NULL,
  PRIMARY KEY (`product_id`),
  INDEX `fk_product_tiers1_idx` (`tier_id` ASC) ,
  CONSTRAINT `fk_product_tiers1`
    FOREIGN KEY (`tier_id`)
    REFERENCES `clientdb`.`tier` (`tier_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `clientdb`.`game`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `clientdb`.`game` (
  `game_id` VARCHAR(10) NOT NULL,
  `rounds` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`game_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `clientdb`.`rounds`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `clientdb`.`rounds` (
  `round_id` VARCHAR(10) NOT NULL,
  `round_number` INT(11) NOT NULL,
  `length` INT(11) NOT NULL,
  `start_time` DATETIME NOT NULL,
  `end_time` DATETIME NOT NULL,
  `game_id` VARCHAR(10) NOT NULL,
  PRIMARY KEY (`round_id`),
  INDEX `fk_rounds_game1_idx` (`game_id` ASC) ,
  CONSTRAINT `fk_rounds_game1`
    FOREIGN KEY (`game_id`)
    REFERENCES `clientdb`.`game` (`game_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `clientdb`.`backlog`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `clientdb`.`backlog` (
  `backlog_id` VARCHAR(15) NOT NULL,
  `amount` VARCHAR(45) NOT NULL,
  `time_stamp` DATETIME NOT NULL,
  `round_id` VARCHAR(10) NOT NULL,
  `product_id` VARCHAR(10) NOT NULL,
  `to` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`backlog_id`),
  UNIQUE INDEX `backlog_id_UNIQUE` (`backlog_id` ASC) ,
  INDEX `fk_backlog_rounds1_idx` (`round_id` ASC) ,
  INDEX `fk_backlog_product1_idx` (`product_id` ASC) ,
  INDEX `fk_backlog_tiers1_idx` (`to` ASC) ,
  CONSTRAINT `fk_backlog_product1`
    FOREIGN KEY (`product_id`)
    REFERENCES `clientdb`.`product` (`product_id`),
  CONSTRAINT `fk_backlog_rounds1`
    FOREIGN KEY (`round_id`)
    REFERENCES `clientdb`.`rounds` (`round_id`),
  CONSTRAINT `fk_backlog_tiers1`
    FOREIGN KEY (`to`)
    REFERENCES `clientdb`.`tier` (`tier_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `clientdb`.`deliver`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `clientdb`.`deliver` (
  `deliver_id` VARCHAR(10) NOT NULL,
  `amount` INT(11) NOT NULL,
  `time_stamp` DATETIME NOT NULL,
  `product_id` VARCHAR(10) NOT NULL,
  `to_tier_id` INT(11) NOT NULL,
  `round_id` VARCHAR(10) NOT NULL,
  PRIMARY KEY (`deliver_id`),
  INDEX `fk_deliver_tiers1_idx` (`to_tier_id` ASC) ,
  INDEX `fk_deliver_rounds1_idx` (`round_id` ASC) ,
  INDEX `fk_deliver_product1_idx` (`product_id` ASC) ,
  CONSTRAINT `fk_deliver_product1`
    FOREIGN KEY (`product_id`)
    REFERENCES `clientdb`.`product` (`product_id`),
  CONSTRAINT `fk_deliver_rounds1`
    FOREIGN KEY (`round_id`)
    REFERENCES `clientdb`.`rounds` (`round_id`),
  CONSTRAINT `fk_deliver_tiers1`
    FOREIGN KEY (`to_tier_id`)
    REFERENCES `clientdb`.`tier` (`tier_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `clientdb`.`inbound`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `clientdb`.`inbound` (
  `inbound_id` VARCHAR(10) NOT NULL,
  `amount` VARCHAR(45) NULL DEFAULT NULL,
  `round_id` VARCHAR(10) NOT NULL,
  `round_id1` VARCHAR(10) NOT NULL,
  `product_id` VARCHAR(10) NOT NULL,
  `tier_id` INT(11) NOT NULL,
  PRIMARY KEY (`inbound_id`),
  INDEX `fk_inbound_rounds1_idx` (`round_id` ASC) ,
  INDEX `fk_inbound_rounds2_idx` (`round_id1` ASC) ,
  INDEX `fk_inbound_product1_idx` (`product_id` ASC) ,
  INDEX `fk_inbound_tiers1_idx` (`tier_id` ASC) ,
  CONSTRAINT `fk_inbound_product1`
    FOREIGN KEY (`product_id`)
    REFERENCES `clientdb`.`product` (`product_id`),
  CONSTRAINT `fk_inbound_rounds1`
    FOREIGN KEY (`round_id`)
    REFERENCES `clientdb`.`rounds` (`round_id`),
  CONSTRAINT `fk_inbound_rounds2`
    FOREIGN KEY (`round_id1`)
    REFERENCES `clientdb`.`rounds` (`round_id`),
  CONSTRAINT `fk_inbound_tiers1`
    FOREIGN KEY (`tier_id`)
    REFERENCES `clientdb`.`tier` (`tier_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `clientdb`.`openorders`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `clientdb`.`openorders` (
  `openorders_id` VARCHAR(15) NOT NULL,
  `amount` VARCHAR(45) NOT NULL,
  `time_stamp` DATETIME NOT NULL,
  `round_id` VARCHAR(10) NOT NULL,
  `product_id` VARCHAR(10) NOT NULL,
  `from_id` INT(11) NOT NULL,
  PRIMARY KEY (`openorders_id`),
  UNIQUE INDEX `opneorders_id_UNIQUE` (`openorders_id` ASC) ,
  INDEX `fk_openorders_rounds1_idx` (`round_id` ASC) ,
  INDEX `fk_openorders_product1_idx` (`product_id` ASC) ,
  INDEX `fk_openorders_tiers1_idx` (`from_id` ASC) ,
  CONSTRAINT `fk_openorders_product1`
    FOREIGN KEY (`product_id`)
    REFERENCES `clientdb`.`product` (`product_id`),
  CONSTRAINT `fk_openorders_rounds1`
    FOREIGN KEY (`round_id`)
    REFERENCES `clientdb`.`rounds` (`round_id`),
  CONSTRAINT `fk_openorders_tiers1`
    FOREIGN KEY (`from_id`)
    REFERENCES `clientdb`.`tier` (`tier_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `clientdb`.`order`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `clientdb`.`order` (
  `order_id` VARCHAR(10) NOT NULL,
  `amount` INT(11) NOT NULL,
  `time_stamp` VARCHAR(45) NOT NULL,
  `product_id` VARCHAR(10) NOT NULL,
  `tier_id` INT(11) NOT NULL,
  `round_id` VARCHAR(10) NOT NULL,
  PRIMARY KEY (`order_id`),
  INDEX `fk_order_product1_idx` (`product_id` ASC) ,
  INDEX `fk_order_tiers1_idx` (`tier_id` ASC) ,
  INDEX `fk_order_rounds1_idx` (`round_id` ASC) ,
  CONSTRAINT `fk_order_product1`
    FOREIGN KEY (`product_id`)
    REFERENCES `clientdb`.`product` (`product_id`),
  CONSTRAINT `fk_order_rounds1`
    FOREIGN KEY (`round_id`)
    REFERENCES `clientdb`.`rounds` (`round_id`),
  CONSTRAINT `fk_order_tiers1`
    FOREIGN KEY (`tier_id`)
    REFERENCES `clientdb`.`tier` (`tier_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `clientdb`.`outbound`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `clientdb`.`outbound` (
  `outbound_id` VARCHAR(10) NOT NULL,
  `amount` INT(11) NULL DEFAULT NULL,
  `round_id` VARCHAR(10) NOT NULL,
  `tier_id` INT(11) NOT NULL,
  `product_id` VARCHAR(10) NOT NULL,
  PRIMARY KEY (`outbound_id`),
  INDEX `fk_outbound_rounds1_idx` (`round_id` ASC) ,
  INDEX `fk_outbound_tiers1_idx` (`tier_id` ASC) ,
  INDEX `fk_outbound_product1_idx` (`product_id` ASC) ,
  CONSTRAINT `fk_outbound_product1`
    FOREIGN KEY (`product_id`)
    REFERENCES `clientdb`.`product` (`product_id`),
  CONSTRAINT `fk_outbound_rounds1`
    FOREIGN KEY (`round_id`)
    REFERENCES `clientdb`.`rounds` (`round_id`),
  CONSTRAINT `fk_outbound_tiers1`
    FOREIGN KEY (`tier_id`)
    REFERENCES `clientdb`.`tier` (`tier_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `clientdb`.`production`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `clientdb`.`production` (
  `production_id` VARCHAR(10) NOT NULL,
  `amount` INT(11) NOT NULL,
  `product_id` VARCHAR(10) NOT NULL,
  `total_production_time` INT(11) NOT NULL,
  `time_stamp` DATETIME NOT NULL,
  `round_id` VARCHAR(10) NOT NULL,
  PRIMARY KEY (`production_id`),
  INDEX `fk_production_rounds1_idx` (`round_id` ASC) ,
  INDEX `fk_production_product1_idx` (`product_id` ASC) ,
  CONSTRAINT `fk_production_product1`
    FOREIGN KEY (`product_id`)
    REFERENCES `clientdb`.`product` (`product_id`),
  CONSTRAINT `fk_production_rounds1`
    FOREIGN KEY (`round_id`)
    REFERENCES `clientdb`.`rounds` (`round_id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `clientdb`.`stock`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `clientdb`.`stock` (
  `stock_id` INT(11) NOT NULL AUTO_INCREMENT,
  `stock_amount` INT(11) NOT NULL,
  `product_id` VARCHAR(10) NOT NULL,
  `round_id` VARCHAR(10) NOT NULL,
  PRIMARY KEY (`stock_id`),
  UNIQUE INDEX `product_id_UNIQUE` (`stock_id` ASC) ,
  INDEX `fk_stock_product_idx` (`product_id` ASC) ,
  INDEX `fk_stock_rounds1_idx` (`round_id` ASC) ,
  CONSTRAINT `fk_stock_product`
    FOREIGN KEY (`product_id`)
    REFERENCES `clientdb`.`product` (`product_id`),
  CONSTRAINT `fk_stock_rounds1`
    FOREIGN KEY (`round_id`)
    REFERENCES `clientdb`.`rounds` (`round_id`))
ENGINE = InnoDB
AUTO_INCREMENT = 5380
DEFAULT CHARACTER SET = utf8;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;



SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

INSERT INTO `tier` (`tier_id`,`company_name`) VALUES ('1','AMK ');
INSERT INTO `tier` (`tier_id`,`company_name`) VALUES ('2','AMD');
INSERT INTO `tier` (`tier_id`,`company_name`) VALUES ('3','Intel');
INSERT INTO `tier` (`tier_id`,`company_name`) VALUES ('4','Ironside');
INSERT INTO `tier` (`tier_id`,`company_name`) VALUES ('5','OEM');
