package models

// sha256,code,name,price,is_discounted,image_url,product_url,category_name
type Product struct {
	Id             string `json:"id,omitempty" validate:"required"`
	Origin         string `json:"origin,omitempty" validate:"required"`
	Code           string `json:"code,omitempty"`
	Name           string `json:"name,omitempty" validate:"required"`
	Price          int    `json:"price,omitempty" validate:"required"`
	MayoristaPrice int    `json:"mayorista_price,omitempty"`
	IsDiscounted   *bool  `json:"is_discounted,omitempty"`
	ImageUrl       string `json:"image_url,omitempty" validate:"required"`
	ProductUrl     string `json:"product_url,omitempty" validate:"required"`
	CategoryName   string `json:"category_name,omitempty" validate:"required"`
}
