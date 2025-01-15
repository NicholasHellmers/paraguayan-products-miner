package controllers

import (
	"context"
	"net/http"
	"time"

	"github.com/NicholasHellmers/Paraguayan-Products-Miner/responses"
	"github.com/gofiber/fiber/v2"
)

func Home(c *fiber.Ctx) error {
	_, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	return c.Status(http.StatusOK).JSON(responses.InfoResponse{Status: http.StatusOK, Message: "success", Data: &fiber.Map{"message": "Welcome to the Paraguayan Products Miner API"}})
}
