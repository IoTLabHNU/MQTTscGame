CREATE DATABASE demodbs;
use demodbs;
CREATE TABLE bytes_recv ( idbytes_recv int(11) NOT NULL AUTO_INCREMENT, total_bytes int(11) NOT NULL, time_stamp datetime NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (idbytes_recv) );
CREATE TABLE cpu_usage ( id_cpu_usage int(11) NOT NULL AUTO_INCREMENT, cpu_per float NOT NULL, time_stamp datetime NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (id_cpu_usage) );
CREATE TABLE packet_lenght ( idpacket_lenght int(11) NOT NULL AUTO_INCREMENT, packet_len int(11) DEFAULT NULL, time_stamp datetime NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (idpacket_lenght) );
CREATE TABLE ram_usage ( idram_usage int(11) NOT NULL AUTO_INCREMENT, ram_usage float NOT NULL, time_stamp datetime NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (idram_usage) );
CREATE TABLE tempreture ( idtempreture int(11) NOT NULL AUTO_INCREMENT, curr_tempreture int(11) NOT NULL, time_stamp datetime NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (idtempreture) );
