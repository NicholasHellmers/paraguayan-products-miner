package routes

import (
	"github.com/NicholasHellmers/Paraguayan-Products-Miner/controllers"
	"github.com/gofiber/fiber/v2"
)

func ProductRoutes(app *fiber.App) {
	app.Post("/product", controllers.CreateProduct)
	app.Post("/products", controllers.CreateProducts)
	app.Get("/product/:productId", controllers.GetAProduct)
	app.Get("/products", controllers.GetAllProducts)
}
