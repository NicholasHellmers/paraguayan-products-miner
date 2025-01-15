package models

import "go.mongodb.org/mongo-driver/bson/primitive"

// md5,code,name,price,is_discounted,image_url,product_url,category_name
type Product struct {
	Id           primitive.ObjectID `json:"id,omitempty"`
	MD5          string             `json:"md5,omitempty"`
	Origin       string             `json:"origin,omitempty" validate:"required"`
	Code         string             `json:"code,omitempty"`
	Name         string             `json:"name,omitempty" validate:"required"`
	Price        int                `json:"price,omitempty" validate:"required"`
	IsDiscounted *bool              `json:"is_discounted,omitempty" validate:"required"`
	ImageUrl     string             `json:"image_url,omitempty" validate:"required"`
	ProductUrl   string             `json:"product_url,omitempty" validate:"required"`
	CategoryName string             `json:"category_name,omitempty" validate:"required"`
}
