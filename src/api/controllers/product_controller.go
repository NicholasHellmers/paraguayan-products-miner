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
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
)

var productCollection *mongo.Collection = configs.GetCollection(configs.DB, "products")
var productValidate = validator.New()

func CreateProduct(c *fiber.Ctx) error {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
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
		Id:           primitive.NewObjectID(),
		MD5:          product.MD5,
		Origin:       product.Origin,
		Name:         product.Name,
		Code:         product.Code,
		Price:        product.Price,
		IsDiscounted: product.IsDiscounted,
		ImageUrl:     product.ImageUrl,
		ProductUrl:   product.ProductUrl,
		CategoryName: product.CategoryName,
	}

	// Check if the product already exists via the MD5 hash
	var existingProduct models.Product
	err := productCollection.FindOne(ctx, bson.M{"md5": newProduct.MD5}).Decode(&existingProduct)
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
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	var products []models.Product
	defer cancel()

	//validate the request body
	if err := c.BodyParser(&products); err != nil {
		return c.Status(http.StatusBadRequest).JSON(responses.ProductResponse{Status: http.StatusBadRequest, Message: "error", Data: &fiber.Map{"error_message": err.Error()}})
	}

	//use the validator library to validate required fields
	for _, product := range products {
		if validationErr := productValidate.Struct(&product); validationErr != nil {
			return c.Status(http.StatusBadRequest).JSON(responses.ProductResponse{Status: http.StatusBadRequest, Message: "error", Data: &fiber.Map{"error_message": validationErr.Error()}})
		}
	}

	// product_id,code,name,price,is_discounted,image_url,product_url,category_name
	var newProducts []interface{}
	for _, product := range products {

		newProduct := models.Product{
			Id:           primitive.NewObjectID(),
			MD5:          product.MD5,
			Origin:       product.Origin,
			Name:         product.Name,
			Code:         product.Code,
			Price:        product.Price,
			IsDiscounted: product.IsDiscounted,
			ImageUrl:     product.ImageUrl,
			ProductUrl:   product.ProductUrl,
			CategoryName: product.CategoryName,
		}

		// If one of the products is invalid, return an error
		if validationErr := productValidate.Struct(&newProduct); validationErr != nil {
			return c.Status(http.StatusBadRequest).JSON(responses.ProductResponse{Status: http.StatusBadRequest, Message: "error", Data: &fiber.Map{"error_message": validationErr.Error()}})
		}

		// Check if the product already exists via the MD5 hash, if it does, update the product
		var existingProduct models.Product
		err := productCollection.FindOne(ctx, bson.M{"md5": newProduct.MD5}).Decode(&existingProduct)
		if err == nil {
			_, err := productCollection.UpdateOne(ctx, bson.M{"md5": newProduct.MD5}, bson.M{"$set": newProduct})
			if err != nil {
				return c.Status(http.StatusInternalServerError).JSON(responses.ProductResponse{Status: http.StatusInternalServerError, Message: "error", Data: &fiber.Map{"error_message": err.Error()}})
			}
			continue
		}

		newProducts = append(newProducts, newProduct)
	}

	result, err := productCollection.InsertMany(ctx, newProducts)
	if err != nil {
		return c.Status(http.StatusInternalServerError).JSON(responses.ProductResponse{Status: http.StatusInternalServerError, Message: "error", Data: &fiber.Map{"error_message": err.Error()}})
	}

	return c.Status(http.StatusCreated).JSON(responses.ProductResponse{Status: http.StatusCreated, Message: "success", Data: &fiber.Map{"success_message": result}})
}

func GetAProduct(c *fiber.Ctx) error {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
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
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
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
