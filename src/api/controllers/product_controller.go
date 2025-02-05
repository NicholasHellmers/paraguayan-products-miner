package controllers

import (
	"context"
	"log"
	"net/http"
	"time"

	"github.com/NicholasHellmers/Paraguayan-Products-Miner/configs"
	"github.com/NicholasHellmers/Paraguayan-Products-Miner/models"
	"github.com/NicholasHellmers/Paraguayan-Products-Miner/responses"
	"github.com/go-playground/validator/v10"
	"github.com/gofiber/fiber/v2"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

var productCollection *mongo.Collection = configs.GetCollection(configs.DB, "products")

func init() {
	// Ensure the index is created only once at startup
	indexModel := mongo.IndexModel{
		Keys: bson.D{{Key: "_id", Value: 1}},
	}

	_, err := productCollection.Indexes().CreateOne(context.Background(), indexModel)
	if err != nil {
		log.Fatal("Could not create index:", err)
	}
}

var productValidate = validator.New()

func CreateProduct(c *fiber.Ctx) error {
	ctx, cancel := context.WithTimeout(context.Background(), 120*time.Second)
	var product models.Product
	defer cancel()

	if err := c.BodyParser(&product); err != nil {
		return c.Status(http.StatusBadRequest).JSON(responses.ProductResponse{
			Status: http.StatusBadRequest, Message: "error", Data: &fiber.Map{"error_message": err.Error()},
		})
	}

	if validationErr := productValidate.Struct(&product); validationErr != nil {
		return c.Status(http.StatusBadRequest).JSON(responses.ProductResponse{
			Status: http.StatusBadRequest, Message: "error", Data: &fiber.Map{"error_message": validationErr.Error()},
		})
	}

	// Insert the product using `_id` instead of `id`
	_, err := productCollection.InsertOne(ctx, bson.M{
		"_id":            product.Id,
		"origin":         product.Origin,
		"name":           product.Name,
		"code":           product.Code,
		"price":          product.Price,
		"mayoristaPrice": product.MayoristaPrice,
		"isDiscounted":   product.IsDiscounted,
		"imageUrl":       product.ImageUrl,
		"productUrl":     product.ProductUrl,
		"categoryName":   product.CategoryName,
	})

	if err != nil {
		return c.Status(http.StatusConflict).JSON(responses.ProductResponse{
			Status: http.StatusConflict, Message: "error", Data: &fiber.Map{"error_message": "Product already exists or insert failed"},
		})
	}

	return c.Status(http.StatusCreated).JSON(responses.ProductResponse{
		Status: http.StatusCreated, Message: "success", Data: &fiber.Map{"success_message": "Product inserted successfully"},
	})
}

func CreateProducts(c *fiber.Ctx) error {
	ctx, cancel := context.WithTimeout(context.Background(), 120*time.Second)
	var products []models.Product
	defer cancel()

	var uniqueProducts = make(map[string]bool)

	if err := c.BodyParser(&products); err != nil {
		return c.Status(http.StatusBadRequest).JSON(responses.ProductResponse{
			Status: http.StatusBadRequest, Message: "error", Data: &fiber.Map{"error_message": err.Error()},
		})
	}

	for _, product := range products {
		if validationErr := productValidate.Struct(&product); validationErr != nil {
			return c.Status(http.StatusBadRequest).JSON(responses.ProductResponse{
				Status: http.StatusBadRequest, Message: "error", Data: &fiber.Map{"error_message": validationErr.Error()},
			})
		}
	}

	var bulkOps []mongo.WriteModel
	for _, product := range products {
		if _, exists := uniqueProducts[product.Id]; exists {
			continue
		}
		uniqueProducts[product.Id] = true

		filter := bson.D{{Key: "_id", Value: product.Id}}
		update := bson.D{{Key: "$set", Value: product}}
		upsert := mongo.NewUpdateOneModel().SetFilter(filter).SetUpdate(update).SetUpsert(true)
		bulkOps = append(bulkOps, upsert)
	}

	if len(bulkOps) > 0 {
		results, err := productCollection.BulkWrite(ctx, bulkOps, options.BulkWrite().SetOrdered(false))
		if err != nil {
			return c.Status(http.StatusInternalServerError).JSON(responses.ProductResponse{
				Status: http.StatusInternalServerError, Message: "error", Data: &fiber.Map{"error_message": err.Error()},
			})
		}
		return c.Status(http.StatusCreated).JSON(responses.ProductResponse{
			Status: http.StatusCreated, Message: "success", Data: &fiber.Map{"success_message": results},
		})
	}

	return c.Status(http.StatusBadRequest).JSON(responses.ProductResponse{
		Status: http.StatusBadRequest, Message: "error", Data: &fiber.Map{"error_message": "No valid products to insert"},
	})
}

func GetAProduct(c *fiber.Ctx) error {
	ctx, cancel := context.WithTimeout(context.Background(), 120*time.Second)
	productId := c.Params("productId")
	var product models.Product
	defer cancel()

	err := productCollection.FindOne(ctx, bson.M{"_id": productId}).Decode(&product)
	if err != nil {
		return c.Status(http.StatusNotFound).JSON(responses.ProductResponse{
			Status: http.StatusNotFound, Message: "error", Data: &fiber.Map{"error_message": "Product not found"},
		})
	}

	return c.Status(http.StatusOK).JSON(responses.ProductResponse{
		Status: http.StatusOK, Message: "success", Data: &fiber.Map{"product": product},
	})
}

func GetAllProducts(c *fiber.Ctx) error {
	ctx, cancel := context.WithTimeout(context.Background(), 120*time.Second)
	var products []models.Product
	defer cancel()

	cursor, err := productCollection.Find(ctx, bson.M{})
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(responses.ProductResponse{
			Status: http.StatusInternalServerError, Message: "error", Data: &fiber.Map{"error_message": err.Error()},
		})
	}

	defer cursor.Close(ctx)
	for cursor.Next(ctx) {
		var product models.Product
		if err := cursor.Decode(&product); err != nil {
			continue
		}
		products = append(products, product)
	}

	return c.Status(http.StatusOK).JSON(responses.ProductResponse{
		Status: http.StatusOK, Message: "success", Data: &fiber.Map{"products": products},
	})
}
