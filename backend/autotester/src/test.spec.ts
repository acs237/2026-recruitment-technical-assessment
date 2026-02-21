const request = require("supertest");

describe("Task 1", () => {
  describe("POST /parse", () => {
    const getTask1 = async (inputStr) => {
      return await request("http://localhost:8080")
        .post("/parse")
        .send({ input: inputStr });
    };

    it("example1", async () => {
      const response = await getTask1("Riz@z RISO00tto!");
      expect(response.body).toStrictEqual({ msg: "Rizz Risotto" });
    });

    it("example2", async () => {
      const response = await getTask1("alpHa-alFRedo");
      expect(response.body).toStrictEqual({ msg: "Alpha Alfredo" });
    });

    it("error case", async () => {
      const response = await getTask1("");
      expect(response.status).toBe(400);
    });
  });
});

describe("Task 2", () => {
  describe("POST /entry", () => {
    const putTask2 = async (data) => {
      return await request("http://localhost:8080").post("/entry").send(data);
    };

    it("Add Ingredients", async () => {
      const entries = [
        { type: "ingredient", name: "Egg", cookTime: 6 },
        { type: "ingredient", name: "Lettuce", cookTime: 1 },
      ];
      for (const entry of entries) {
        const resp = await putTask2(entry);
        expect(resp.status).toBe(200);
        expect(resp.body).toStrictEqual({});
      }
    });

    it("Add Recipe", async () => {
      const meatball = {
        type: "recipe",
        name: "Meatball",
        requiredItems: [{ name: "Beef", quantity: 1 }],
      };
      const resp1 = await putTask2(meatball);
      expect(resp1.status).toBe(200);
    });

    it("Congratulations u burnt the pan pt2", async () => {
      const resp = await putTask2({
        type: "ingredient",
        name: "beef",
        cookTime: -1,
      });
      expect(resp.status).toBe(400);
    });

    it("Congratulations u burnt the pan pt3", async () => {
      const resp = await putTask2({
        type: "pan",
        name: "pan",
        cookTime: 20,
      });
      expect(resp.status).toBe(400);
    });

    it("Unique names", async () => {
      const resp = await putTask2({
        type: "ingredient",
        name: "Beef",
        cookTime: 10,
      });
      expect(resp.status).toBe(200);

      const resp2 = await putTask2({
        type: "ingredient",
        name: "Beef",
        cookTime: 8,
      });
      expect(resp2.status).toBe(400);

      const resp3 = await putTask2({
        type: "recipe",
        name: "Beef",
        cookTime: 8,
      });
      expect(resp3.status).toBe(400);
    });
    it("One element per name for requiredItems", async () => {
      const resp = await putTask2({
        type: "recipe",
        name: "Beef",
        requiredItems: [{ name: "Beef", quantity: 1 }, { name: "Beef", quantity: 4 }],
      });
      expect(resp.status).toBe(400);
    });
  });
});

describe("Task 3", () => {
  describe("GET /summary", () => {
    const postEntry = async (data) => {
      return await request("http://localhost:8080").post("/entry").send(data);
    };

    const getTask3 = async (name) => {
      return await request("http://localhost:8080").get(
        `/summary?name=${name}`
      );
    };

    it("What is bro doing - Get empty cookbook", async () => {
      const resp = await getTask3("nothing");
      expect(resp.status).toBe(400);
    });

    it("What is bro doing - Get ingredient", async () => {
      const resp = await postEntry({
        type: "ingredient",
        name: "beeff",
        cookTime: 2,
      });
      expect(resp.status).toBe(200);

      const resp2 = await getTask3("beeff");
      expect(resp2.status).toBe(400);
    });

    it("Unknown missing item", async () => {
      const cheese = {
        type: "recipe",
        name: "Cheese",
        requiredItems: [{ name: "Not Real", quantity: 1 }],
      };
      const resp1 = await postEntry(cheese);
      expect(resp1.status).toBe(200);

      const resp2 = await getTask3("Cheese");
      expect(resp2.status).toBe(400);
    });

    it("Bro cooked", async () => {
      const meatball = {
        type: "recipe",
        name: "Skibidi",
        requiredItems: [{ name: "Bruh", quantity: 1 }],
      };
      const resp1 = await postEntry(meatball);
      expect(resp1.status).toBe(200);

      const resp2 = await postEntry({
        type: "ingredient",
        name: "Bruh",
        cookTime: 2,
      });
      expect(resp2.status).toBe(200);

      const resp3 = await getTask3("Skibidi");
      expect(resp3.status).toBe(200);
    });

    it("Skibidi Spaghetti - nested recipe summary", async () => {
      const entries = [
        { type: "ingredient", name: "Beef", cookTime: 5 },
        { type: "ingredient", name: "Egg", cookTime: 3 },
        { type: "ingredient", name: "Flour", cookTime: 0 },
        { type: "ingredient", name: "Tomato", cookTime: 2 },
        {
          type: "recipe",
          name: "Meatball",
          requiredItems: [
            { name: "Beef", quantity: 2 },
            { name: "Egg", quantity: 1 },
          ],
        },
        {
          type: "recipe",
          name: "Pasta",
          requiredItems: [
            { name: "Flour", quantity: 3 },
            { name: "Egg", quantity: 1 },
          ],
        },
        {
          type: "recipe",
          name: "Skibidi Spaghetti",
          requiredItems: [
            { name: "Meatball", quantity: 3 },
            { name: "Pasta", quantity: 1 },
            { name: "Tomato", quantity: 2 },
          ],
        },
      ];

      for (const entry of entries) {
        const resp = await postEntry(entry);
        expect(resp.status).toBe(200);
      }

      const resp = await getTask3("Skibidi Spaghetti");
      expect(resp.status).toBe(200);
      // result matching
      expect(resp.body.name).toBe("Skibidi Spaghetti");
      expect(resp.body.cookTime).toBe(46);
      expect(resp.body.ingredients).toHaveLength(4);
      expect(resp.body.ingredients).toEqual(
        expect.arrayContaining([
          { name: "Beef", quantity: 6 },
          { name: "Flour", quantity: 3 },
          { name: "Egg", quantity: 4 },
          { name: "Tomato", quantity: 2 },
        ])
      );
    });
  });
});
