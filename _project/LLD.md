

Models
    - Product List
        - user (fk)
        - name
     
    - Product Info
        - user (fk)
        - title
        - review
        - rating ...


1. ProductList (List Name ): Viewset
    - CREATE 
    - DELETE 
    - GET

2. ProductInfo ()
    - CREATE 
    - GET

3. Export Excel or csv

4. Run Audit need a list 

5. Analyse Audit and run reaudit for asins which could not load due to reasons


6. === Audit ===

- view -> tasks.dealy() -> RunAudit (Orchrastion Layer)

- RunAudit
    - get_product_infos(Product List Id) {which will help to collect the asin to Audit}
    - CreateBrowser()
    -  AmazonScrapingLogic


reAudit of supression asins