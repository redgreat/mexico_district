CREATE TABLE `basic_district_mexico` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `code` varchar(5) DEFAULT NULL COMMENT '编码',
  `name` varchar(100) DEFAULT NULL COMMENT '名称',
  `parent_code` varchar(5) DEFAULT NULL COMMENT '上级名称',
  `level_no` smallint DEFAULT NULL COMMENT '行政等级(1州2乡镇)',
  PRIMARY KEY (`id`),
  KEY `non_code` (`code`),
  KEY `non_name` (`name`),
  KEY `non_parent_code` (`parent_code`),
  KEY `non_level_no` (`level_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='墨西哥行政区划';

truncate table basic_district_mexico;
INSERT INTO basic_district_mexico(code,`name`,parent_code,level_no)
SELECT DISTINCT cve_ent,nom_ent,NULL,1
FROM mexico_admin_divisions;

INSERT INTO basic_district_mexico(code,`name`,parent_code,level_no)
SELECT cvegeo,nomgeo,cve_ent,2
FROM mexico_admin_divisions
ORDER BY 3,1;

SELECT b.name,a.name
FROM basic_district_mexico a,
basic_district_mexico b
WHERE b.code=a.parent_code
GROUP BY a.name
HAVING COUNT(1)>1
ORDER BY 1;

SELECT b.name,a.name
FROM basic_district_mexico a,
basic_district_mexico b
WHERE b.code=a.parent_code
AND a.name = 'San Fernando';