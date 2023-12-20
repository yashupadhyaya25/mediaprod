MYSQL Table Create Scripts

**INVOICE DESCRIPTION** 

CREATE TABLE `invoice_description` (
  `CODE` text COLLATE utf8mb4_unicode_ci,
  `DESCRIPTION` text COLLATE utf8mb4_unicode_ci,
  `QUANTITY` text COLLATE utf8mb4_unicode_ci,
  `PER_UNIT_PRICE` text COLLATE utf8mb4_unicode_ci,
  `TOTAL_AMOUNT` text COLLATE utf8mb4_unicode_ci,
  `INVOICE_DATE` text COLLATE utf8mb4_unicode_ci,
  `PDF_NAME` text COLLATE utf8mb4_unicode_ci,
  `INVOICE_TYPE` text COLLATE utf8mb4_unicode_ci,
  `UNIQUE_IDENTIFICATION_NUMBER` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `INVOICE_FROM` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `CREATED_ON` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `SYSTEM_NAME` text COLLATE utf8mb4_unicode_ci,
  `RESTAURANT_NAME` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL
)

**INVOICE TOTAL**

CREATE TABLE `invoice_total` (
  `TOTAL_TVA` text COLLATE utf8mb4_unicode_ci,
  `TOTAL_HT` text COLLATE utf8mb4_unicode_ci,
  `TOTAL_TTC` text COLLATE utf8mb4_unicode_ci,
  `INVOICE_DATE` text COLLATE utf8mb4_unicode_ci,
  `PDF_NAME` text COLLATE utf8mb4_unicode_ci,
  `INVOICE_TYPE` text COLLATE utf8mb4_unicode_ci,
  `UNIQUE_IDENTIFICATION_NUMBER` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `INVOICE_FROM` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `CREATED_ON` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `SYSTEM_NAME` text COLLATE utf8mb4_unicode_ci,
  `RESTAURANT_NAME` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL
)

**PDF AUDIT**

CREATE TABLE `logs` (
  `PDF_NAME` varchar(500) DEFAULT NULL,
  `STATUS` varchar(45) DEFAULT NULL,
  `ERROR_MESSAGE` longtext DEFAULT NULL,
  `CREATED_TIME` datetime DEFAULT NULL,
  `INVOICE_FROM` varchar(45) DEFAULT NULL
)

**PRODUCT_MAPPING**

CREATE TABLE `PRODUCT_MAPPING` (
  `DESCRIPTION` text DEFAULT NULL,
  `L` text DEFAULT NULL,
  `ML` text DEFAULT NULL,
  `KG` text DEFAULT NULL,
  `GM` text DEFAULT NULL,
  `PC` text DEFAULT NULL,
  `PRODUCT_GROUP` text DEFAULT NULL
)
