
/*
 * This file is an example of how to seed data into a MongoDB database.
 * This file is meant to be run in the MongoDB shell so it can be used to seed data and create the collections that
 * are going to go into a database.
 * 
 * This is run by the mongodb container when it starts up. The mongodb container is defined in the docker-compose.yml file.
 * Make sure to change the name of this file to "init.js" and update the values in the file to match the values in the
 * .env file. 
 */

// Authenticate as the root user
db = db.getSiblingDB("admin"); // Change this to the name of the database you want to use dictated in the .env file
db.auth("admin", "password"); // Change this to the username and password you want to use dictated in the .env file

// Switch to the specified database
db = db.getSiblingDB("mongo");

// Create collections
db.createCollection("users");
db.createCollection("products");

// Seed data for "users" collection
db.users.insertMany([
  {
    name: "Nicholas Hellmers",
    location: "Boulder, CO",
    title: "Software Engineer"
  },
  {
    name: "Abby Barnes",
    location: "Asuncion, PY",
    title: "Roku Developer"
  }
]);
