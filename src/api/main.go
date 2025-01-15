package main

import (
	"github.com/NicholasHellmers/Paraguayan-Products-Miner/configs"
	"github.com/NicholasHellmers/Paraguayan-Products-Miner/routes"
	"github.com/gofiber/fiber/v2"
)

func main() {
	app := fiber.New()

	//run database
	configs.ConnectDB()

	routes.InfoRoutes(app)

	routes.UserRoute(app)

	routes.ProductRoutes(app)

	app.Listen(":8080")
}