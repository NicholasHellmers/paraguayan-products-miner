package controllers

import (
	"context"
	"net/http"
	"time"

	"github.com/NicholasHellmers/Paraguayan-Products-Miner/configs"
	"github.com/NicholasHellmers/Paraguayan-Products-Miner/models"
	"github.com/NicholasHellmers/Paraguayan-Products-Miner/responses"
	"github.com/go-playground/validator/v10"
	"github.com/gofiber/fiber/v2"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
)

var productCollection *mongo.Collection = configs.GetCollection(configs.DB, "products")
var productValidate = validator.New()

func CreateProduct(c *fiber.Ctx) error {
	ctx, cancel := context.WithTimeout(context.Background(), 120*time.Second)
	var product models.Product
	defer cancel()

	//validate the request body
	if err := c.BodyParser(&product); err != nil {
		return c.Status(http.StatusBadRequest).JSON(responses.ProductResponse{Status: http.StatusBadRequest, Message: "error", Data: &fiber.Map{"error_message": err.Error()}})
	}

	//use the validator library to validate required fields
	if validationErr := productValidate.Struct(&product); validationErr != nil {
		return c.Status(http.StatusBadRequest).JSON(responses.ProductResponse{Status: http.StatusBadRequest, Message: "error", Data: &fiber.Map{"error_message": validationErr.Error()}})
	}

	// product_id,code,name,price,is_discounted,image_url,product_url,category_name
	newProduct := models.Product{
		Id:           product.Id,
		Origin:       product.Origin,
		Name:         product.Name,
		Code:         product.Code,
		Price:        product.Price,
		IsDiscounted: product.IsDiscounted,
		ImageUrl:     product.ImageUrl,
		ProductUrl:   product.ProductUrl,
		CategoryName: product.CategoryName,
	}

	// Check if the product already exists via the sha256 hash
	var existingProduct models.Product
	err := productCollection.FindOne(ctx, bson.M{"id": newProduct.Id}).Decode(&existingProduct)
	if err == nil {
		return c.Status(http.StatusConflict).JSON(responses.ProductResponse{Status: http.StatusConflict, Message: "error", Data: &fiber.Map{"error_message": "Product already exists"}})
	}

	result, err := productCollection.InsertOne(ctx, newProduct)
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(responses.ProductResponse{Status: http.StatusInternalServerError, Message: "error", Data: &fiber.Map{"error_message": err.Error()}})
	}

	return c.Status(http.StatusCreated).JSON(responses.ProductResponse{Status: http.StatusCreated, Message: "success", Data: &fiber.Map{"success_message": result}})
}

func CreateProducts(c *fiber.Ctx) error {
	ctx, cancel := context.WithTimeout(context.Background(), 120*time.Second)
	var products []models.Product
	defer cancel()

	// Remove all duplicate products based on id
	var uniqueProducts map[string]bool = make(map[string]bool)

	// Validate the request body
	if err := c.BodyParser(&products); err != nil {
		return c.Status(http.StatusBadRequest).JSON(responses.ProductResponse{Status: http.StatusBadRequest, Message: "error", Data: &fiber.Map{"error_message": err.Error()}})
	}

	// Validate required fields
	for _, product := range products {
		if validationErr := productValidate.Struct(&product); validationErr != nil {
			return c.Status(http.StatusBadRequest).JSON(responses.ProductResponse{Status: http.StatusBadRequest, Message: "error", Data: &fiber.Map{"error_message": validationErr.Error()}})
		}
	}

	// Prepare products for bulk insert
	var bulkOps []mongo.WriteModel
	for _, product := range products {
		// Check for duplicate by id
		if _, exists := uniqueProducts[product.Id]; exists {
			// Skip this product if it's already processed
			continue
		}
		uniqueProducts[product.Id] = true

		// Create the upsert operation
		bulkOps = append(bulkOps, mongo.NewUpdateOneModel().
			SetFilter(bson.M{"id": product.Id}). // Match on product id
			SetUpdate(bson.M{"$set": product}).  // Update fields if document exists
			SetUpsert(true))                     // If document doesn't exist, insert it
	}

	// Execute the bulk write operation if there are any operations
	if len(bulkOps) > 0 {
		result, err := productCollection.BulkWrite(ctx, bulkOps)
		if err != nil {
			return c.Status(http.StatusInternalServerError).JSON(responses.ProductResponse{
				Status:  http.StatusInternalServerError,
				Message: "error",
				Data:    &fiber.Map{"error_message": err.Error()},
			})
		}
		return c.Status(http.StatusCreated).JSON(responses.ProductResponse{
			Status:  http.StatusCreated,
			Message: "success",
			Data:    &fiber.Map{"success_message": result},
		})
	}

	// Return a response if no valid products were processed
	return c.Status(http.StatusBadRequest).JSON(responses.ProductResponse{
		Status:  http.StatusBadRequest,
		Message: "error",
		Data:    &fiber.Map{"error_message": "no valid products to insert"},
	})
}

func GetAProduct(c *fiber.Ctx) error {
	ctx, cancel := context.WithTimeout(context.Background(), 120*time.Second)
	productId := c.Params("productId")
	var product models.Product
	defer cancel()

	err := productCollection.FindOne(ctx, bson.M{"id": productId}).Decode(&product)
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(responses.ProductResponse{Status: http.StatusInternalServerError, Message: "error", Data: &fiber.Map{"error_message": err.Error()}})
	}

	return c.Status(http.StatusOK).JSON(responses.ProductResponse{Status: http.StatusOK, Message: "success", Data: &fiber.Map{"product": product}})
}

func GetAllProducts(c *fiber.Ctx) error {
	ctx, cancel := context.WithTimeout(context.Background(), 120*time.Second)
	var products []models.Product
	defer cancel()

	cursor, err := productCollection.Find(ctx, bson.M{})
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(responses.ProductResponse{Status: http.StatusInternalServerError, Message: "error", Data: &fiber.Map{"error_message": err.Error()}})
	}

	defer cursor.Close(ctx)
	for cursor.Next(ctx) {
		var product models.Product
		cursor.Decode(&product)
		products = append(products, product)
	}

	return c.Status(http.StatusOK).JSON(responses.ProductResponse{Status: http.StatusOK, Message: "success", Data: &fiber.Map{"products": products}})
}
