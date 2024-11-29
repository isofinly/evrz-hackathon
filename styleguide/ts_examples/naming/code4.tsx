import { Product } from "@/entities/CardsGallary/model/types/types";
import { Endpoints } from "@/shared/utils";
import { createStore, createEffect } from "effector";

export const $filters = createStore<ProductFilters>({
  limit: 10,
  query: "",
  category: "all" as Category,
  skip: 0,
});
type Props = {
  setLoading: (value: boolean) => void;
  filters: ProductFilters;
};
