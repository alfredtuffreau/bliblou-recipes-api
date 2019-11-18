CREATE DATABASE recipes_db;

CREATE TABLE ingredients (
  id INT AUTO_INCREMENT NOT NULL,
  name VARCHAR(255) NOT NULL,
  uuid CHAR(16) NOT NULL,
  PRIMARY KEY (id)
);
CREATE TABLE units (
  id INT AUTO_INCREMENT NOT NULL,
  name VARCHAR(255) NOT NULL,
  uuid CHAR(16) NOT NULL,
  PRIMARY KEY (id)
);
CREATE TABLE ingredients_list (
  recipeUuid CHAR(16) NOT NULL,
  ingredientIndex INT NOT NULL,
  quantity DECIMAL(5,2) NOT NULL,
  unitId INT NOT NULL,
  ingredientId INT NOT NULL,
  FOREIGN KEY (unitId) REFERENCES units(id),
  FOREIGN KEY (ingredientId) REFERENCES ingredients(id),
  CONSTRAINT tb_PK PRIMARY KEY (unitId, ingredientId)
);