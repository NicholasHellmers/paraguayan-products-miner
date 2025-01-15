package routes

import (
	"github.com/NicholasHellmers/Paraguayan-Products-Miner/controllers"
	"github.com/gofiber/fiber/v2"
)

func InfoRoutes(app *fiber.App) {
	app.Get("/", controllers.Home)
}
