package models

// sha256,code,name,price,is_discounted,image_url,product_url,category_name
type Product struct {
	Id             string `json:"id,omitempty" bson:"_id" validate:"required"`
	Origin         string `json:"origin,omitempty" bson:"origin" validate:"required"`
	Code           string `json:"code,omitempty" bson:"code"`
	Name           string `json:"name,omitempty" bson:"name" validate:"required"`
	Price          int    `json:"price,omitempty" bson:"price" validate:"required"`
	MayoristaPrice int    `json:"mayorista_price,omitempty" bson:"mayorista_price"`
	IsDiscounted   *bool  `json:"is_discounted,omitempty" bson:"is_discounted"`
	ImageUrl       string `json:"image_url,omitempty" bson:"image_url" validate:"required"`
	ProductUrl     string `json:"product_url,omitempty" bson:"product_url" validate:"required"`
	CategoryName   string `json:"category_name,omitempty" bson:"category_name" validate:"required"`
}
