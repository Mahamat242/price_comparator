import { useState } from "react";
import Header from "./header";

function App() {
  const [searchTerm, setSearchTerm] = useState("");
  const [liste, setListe] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // filtres
  const [sources, setSources] = useState({ jumia: true, expat: true });
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [category, setCategory] = useState("");
  const [sortBy, setSortBy] = useState("default");

  // comparaison
  const [selectedIds, setSelectedIds] = useState([]);
  const [compareData, setCompareData] = useState(null);
  const [isComparing, setIsComparing] = useState(false);
  const [compareLoading, setCompareLoading] = useState(false);

  // recuperation des produits avec filtres
  const fetchProducts = async (query = searchTerm, currentFilters = {}) => {
    setLoading(true);
    setError(null);

    const activeSources = currentFilters.sources ?? sources;
    const currentMin = currentFilters.minPrice ?? minPrice;
    const currentMax = currentFilters.maxPrice ?? maxPrice;
    const currentCat = currentFilters.category ?? category;

    try {
      const params = new URLSearchParams();
      if (query) params.append("q", query);

      // filtre par source
      if (activeSources.jumia && !activeSources.expat) {
        params.append("source", "Jumia");
      } else if (!activeSources.jumia && activeSources.expat) {
        params.append("source", "Expat Dakar");
      }

      if (currentMin) params.append("min_price", currentMin);
      if (currentMax) params.append("max_price", currentMax);
      if (currentCat && currentCat !== "Toutes les catégories") {
        params.append("category", currentCat);
      }

      const response = await fetch(
        `http://localhost:8000/api/products/?${params.toString()}`
      );

      if (!response.ok) {
        throw new Error("Erreur lors de la récupération des données");
      }

      const data = await response.json();
      setListe(data.products || []);
      setTotalCount(data.total || (data.products ? data.products.length : 0));
    } catch (err) {
      console.error("Erreur API :", err);
      setError("Impossible de contacter le serveur backend");
    } finally {
      setLoading(false);
    }
  };

  // declenche la recherche
  const handleSearch = (query) => {
    setSearchTerm(query);
    fetchProducts(query);
  };

  // applique les filtres
  const handleFilterSubmit = (e) => {
    e.preventDefault();
    fetchProducts(searchTerm);
  };

  // reset filtres
  const handleResetFilters = () => {
    const defaultSources = { jumia: true, expat: true };
    setSources(defaultSources);
    setMinPrice("");
    setMaxPrice("");
    setCategory("");
    setSortBy("default");
    fetchProducts(searchTerm, {
      sources: defaultSources,
      minPrice: "",
      maxPrice: "",
      category: "",
    });
  };

  // selection pour le comparateur
  const toggleSelectProduct = (id) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  // appel api pour comparer
  const handleCompare = async () => {
    if (selectedIds.length === 0) return;
    setCompareLoading(true);
    setIsComparing(true);

    try {
      const queryParams = selectedIds.map((id) => `ids=${id}`).join("&");
      const res = await fetch(`http://localhost:8000/api/products/compare?${queryParams}`);
      if (!res.ok) throw new Error("Erreur de comparaison");
      const data = await res.json();
      setCompareData(data);
    } catch (err) {
      console.error("Erreur lors de la comparaison:", err);
    } finally {
      setCompareLoading(false);
    }
  };

  // tri local
  const sortedProducts = [...liste].sort((a, b) => {
    if (sortBy === "price_asc") return (a.price || 0) - (b.price || 0);
    if (sortBy === "price_desc") return (b.price || 0) - (a.price || 0);
    return 0;
  });

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 flex flex-col font-['Inter',sans-serif]">
      <Header onSearch={handleSearch} />

      <main className="max-w-7xl w-full mx-auto px-4 sm:px-6 py-8 flex flex-col md:flex-row gap-8 flex-1">
        {/* sidebar filtres */}
        <aside className="w-full md:w-64 shrink-0">
          <form
            onSubmit={handleFilterSubmit}
            className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-6 sticky top-24"
          >
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
                <svg
                  className="w-4 h-4 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
                  />
                </svg>
                Filtres
              </h3>
              {(minPrice || maxPrice || category || !sources.jumia || !sources.expat) && (
                <button
                  type="button"
                  onClick={handleResetFilters}
                  className="text-xs text-blue-600 hover:text-blue-800 font-medium transition cursor-pointer"
                >
                  Effacer
                </button>
              )}
            </div>

            {/* sources */}
            <div className="space-y-3">
              <label className="text-xs font-bold text-slate-600 uppercase tracking-wider block">
                Source
              </label>
              <div className="space-y-2 text-sm">
                <label className="flex items-center gap-2.5 cursor-pointer text-slate-700 hover:text-slate-900 transition">
                  <input
                    type="checkbox"
                    checked={sources.jumia}
                    onChange={(e) =>
                      setSources((prev) => ({ ...prev, jumia: e.target.checked }))
                    }
                    className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-slate-300 cursor-pointer"
                  />
                  <span>Jumia Sénégal</span>
                </label>
                <label className="flex items-center gap-2.5 cursor-pointer text-slate-700 hover:text-slate-900 transition">
                  <input
                    type="checkbox"
                    checked={sources.expat}
                    onChange={(e) =>
                      setSources((prev) => ({ ...prev, expat: e.target.checked }))
                    }
                    className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-slate-300 cursor-pointer"
                  />
                  <span>Expat Dakar</span>
                </label>
              </div>
            </div>

            {/* prix */}
            <div className="space-y-3">
              <label className="text-xs font-bold text-slate-600 uppercase tracking-wider block">
                Prix (FCFA)
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  placeholder="Min"
                  value={minPrice}
                  onChange={(e) => setMinPrice(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10 outline-none transition"
                />
                <span className="text-slate-400 text-xs">-</span>
                <input
                  type="number"
                  placeholder="Max"
                  value={maxPrice}
                  onChange={(e) => setMaxPrice(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10 outline-none transition"
                />
              </div>
            </div>

            {/* categories */}
            <div className="space-y-3">
              <label className="text-xs font-bold text-slate-600 uppercase tracking-wider block">
                Catégorie
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10 outline-none transition cursor-pointer"
              >
                <option value="">Toutes les catégories</option>
                <option value="Electronique">Électronique</option>
                <option value="Téléphones">Téléphones & Tablettes</option>
                <option value="Informatique">Informatique & PC</option>
                <option value="Véhicules">Véhicules & Autos</option>
                <option value="Maison">Maison & Déco</option>
                <option value="Mode">Mode & Beauté</option>
              </select>
            </div>

            {/* bouton submit */}
            <button
              type="submit"
              className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 active:scale-[0.98] text-white font-medium text-sm rounded-xl shadow-sm transition-all cursor-pointer"
            >
              Appliquer les filtres
            </button>
          </form>
        </aside>

        {/* liste des resultats */}
        <section className="flex-1 space-y-6 min-w-0">
          {/* infos et tri */}
          <div className="bg-white px-5 py-3.5 rounded-2xl border border-slate-200 shadow-xs flex flex-col sm:flex-row justify-between items-center gap-3">
            <p className="text-sm text-slate-600">
              {loading ? (
                <span>Recherche en cours...</span>
              ) : (
                <>
                  <strong className="text-slate-900 font-bold">{totalCount}</strong>{" "}
                  produit{totalCount > 1 ? "s" : ""} trouvé{totalCount > 1 ? "s" : ""}
                  {searchTerm && (
                    <span>
                      {" "}
                      pour "
                      <span className="font-semibold text-blue-600">
                        {searchTerm}
                      </span>
                      "
                    </span>
                  )}
                </>
              )}
            </p>

            {/* menu tri */}
            <div className="flex items-center gap-2">
              <label htmlFor="sort" className="text-xs font-semibold text-slate-500">
                Trier par :
              </label>
              <select
                id="sort"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="text-sm bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 text-slate-700 focus:border-blue-500 focus:bg-white outline-none cursor-pointer transition"
              >
                <option value="default">Pertinence / Récent</option>
                <option value="price_asc">Prix : Croissant</option>
                <option value="price_desc">Prix : Décroissant</option>
              </select>
            </div>
          </div>

          {/* erreur */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm text-center">
              {error}
            </div>
          )}

          {/* loading */}
          {loading && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3, 4, 5, 6].map((n) => (
                <div
                  key={n}
                  className="bg-white rounded-2xl p-4 border border-slate-100 shadow-xs animate-pulse space-y-3"
                >
                  <div className="bg-slate-200 h-44 rounded-xl"></div>
                  <div className="h-4 bg-slate-200 rounded w-1/3"></div>
                  <div className="h-4 bg-slate-200 rounded w-4/5"></div>
                  <div className="h-6 bg-slate-200 rounded w-1/2 mt-4"></div>
                </div>
              ))}
            </div>
          )}

          {/* cartes produits */}
          {!loading && sortedProducts.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {sortedProducts.map((product) => {
                const isJumia = product.source?.toLowerCase().includes("jumia");
                const isSelected = selectedIds.includes(product.id);

                return (
                  <div
                    key={product.id}
                    className={`group bg-white rounded-2xl shadow-xs hover:shadow-lg transition-all duration-200 p-4 flex flex-col justify-between border ${isSelected
                      ? "border-blue-500 ring-2 ring-blue-500/20 shadow-md"
                      : "border-slate-200/80 hover:border-blue-200"
                      }`}
                  >
                    <div>
                      {/* image */}
                      <div className="relative bg-slate-50 rounded-xl overflow-hidden mb-3 aspect-4/3 flex items-center justify-center p-2">
                        {product.image_url ? (
                          <img
                            src={product.image_url}
                            alt={product.title}
                            className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-300"
                            loading="lazy"
                          />
                        ) : (
                          <div className="text-slate-300 text-xs">Pas d'image</div>
                        )}
                        {/* badge source */}
                        <span
                          className={`absolute top-2.5 left-2.5 text-[11px] font-bold px-2.5 py-1 rounded-full uppercase shadow-xs ${isJumia
                            ? "bg-amber-100 text-amber-800 border border-amber-200"
                            : "bg-indigo-100 text-indigo-800 border border-indigo-200"
                            }`}
                        >
                          {product.source}
                        </span>
                      </div>

                      {/* titre */}
                      <h3
                        title={product.title}
                        className="font-semibold text-slate-900 text-sm line-clamp-2 group-hover:text-blue-600 transition-colors"
                      >
                        {product.title}
                      </h3>
                    </div>

                    {/* prix et boutons */}
                    <div className="mt-4 pt-3 border-t border-slate-100 space-y-3">
                      <div className="flex items-baseline justify-between">
                        <span className="text-[11px] text-slate-500 uppercase font-semibold">Prix</span>
                        <span className="font-extrabold text-base text-emerald-600 tracking-tight">
                          {product.price
                            ? `${Number(product.price).toLocaleString()} ${product.currency || "FCFA"
                            }`
                            : "Non communiqué"}
                        </span>
                      </div>

                      <div className="flex items-center justify-between gap-2 pt-1">
                        <label className="flex items-center gap-2 cursor-pointer select-none text-xs font-medium text-slate-600 hover:text-slate-900 transition">
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={() => toggleSelectProduct(product.id)}
                            className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-slate-300 cursor-pointer"
                          />
                          <span>Comparer</span>
                        </label>

                        <a
                          href={product.product_url}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg transition shadow-xs hover:shadow active:scale-95"
                        >
                          Voir l'offre
                          <svg
                            className="w-3.5 h-3.5"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                            />
                          </svg>
                        </a>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* aucun resultat */}
          {!loading && sortedProducts.length === 0 && !error && (
            <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center space-y-3">
              <div className="w-12 h-12 rounded-full bg-slate-100 text-slate-400 mx-auto flex items-center justify-center">
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </div>
              <h4 className="font-bold text-slate-800">
                {searchTerm
                  ? `Aucun résultat pour "${searchTerm}"`
                  : "Lancez une recherche pour voir les produits"}
              </h4>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                {searchTerm
                  ? "Essayez de modifier vos filtres (prix, catégorie, source) ou d'utiliser d'autres mots-clés."
                  : "Tapez le nom d'un produit dans la barre de recherche en haut pour comparer les prix entre Jumia et Expat Dakar."}
              </p>
            </div>
          )}
        </section>
      </main>

      {/* barre flottante comparaison */}
      {selectedIds.length > 0 && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-slate-900/95 backdrop-blur-md text-white px-6 py-3.5 rounded-full shadow-2xl flex items-center gap-4 z-40 border border-slate-700 animate-in fade-in slide-in-from-bottom-4 duration-300">
          <span className="text-xs font-medium">
            <strong className="text-blue-400 font-bold text-sm">
              {selectedIds.length}
            </strong>{" "}
            produit{selectedIds.length > 1 ? "s" : ""} sélectionné{selectedIds.length > 1 ? "s" : ""}
          </span>
          <button
            onClick={() => setSelectedIds([])}
            className="text-xs text-slate-400 hover:text-white transition cursor-pointer"
          >
            Vider
          </button>
          <button
            onClick={handleCompare}
            disabled={compareLoading}
            className="bg-blue-600 hover:bg-blue-500 active:scale-95 text-white text-xs font-semibold px-4 py-2 rounded-full transition shadow-md flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
          >
            {compareLoading ? "Calcul..." : "Comparer côte à côte"}
            <svg
              className="w-3.5 h-3.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5l7 7-7 7"
              />
            </svg>
          </button>
        </div>
      )}

      {/* modale comparaison */}
      {isComparing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs animate-in fade-in">
          <div className="bg-white w-full max-w-4xl max-h-[90vh] rounded-3xl shadow-2xl overflow-hidden flex flex-col border border-slate-100">
            {/* header modale */}
            <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
              <div>
                <h2 className="text-lg font-bold text-slate-900">
                  Comparaison des offres
                </h2>
                <p className="text-xs text-slate-500">
                  Analyse détaillée des prix et caractéristiques
                </p>
              </div>
              <button
                onClick={() => {
                  setIsComparing(false);
                  setCompareData(null);
                }}
                className="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition cursor-pointer"
              >
                ✕
              </button>
            </div>

            {/* contenu */}
            <div className="p-6 overflow-y-auto space-y-6">
              {compareLoading && (
                <div className="text-center py-12 text-blue-600 animate-pulse font-medium">
                  Chargement de la comparaison...
                </div>
              )}

              {compareData && (
                <>
                  {/* stats */}
                  {compareData.metrics && (
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 bg-blue-50/70 border border-blue-100 rounded-2xl p-4 text-center">
                      <div>
                        <span className="text-xs text-slate-500 font-medium block">
                          Meilleur Prix
                        </span>
                        <span className="text-lg font-black text-emerald-600">
                          {compareData.metrics.min_price?.toLocaleString()} FCFA
                        </span>
                      </div>
                      <div>
                        <span className="text-xs text-slate-500 font-medium block">
                          Prix Maximum
                        </span>
                        <span className="text-lg font-black text-slate-800">
                          {compareData.metrics.max_price?.toLocaleString()} FCFA
                        </span>
                      </div>
                      <div>
                        <span className="text-xs text-slate-500 font-medium block">
                          Économie potentielle
                        </span>
                        <span className="text-lg font-black text-blue-600">
                          {compareData.metrics.price_difference > 0
                            ? `${compareData.metrics.price_difference?.toLocaleString()} FCFA`
                            : "Prix identiques"}
                        </span>
                      </div>
                    </div>
                  )}

                  {/* tableau comparatif */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {compareData.compared_products?.map((item, index) => {
                      const isBestPrice =
                        item.price === compareData.metrics?.min_price;
                      return (
                        <div
                          key={item.id || index}
                          className={`rounded-2xl p-4 border flex flex-col justify-between ${isBestPrice
                            ? "bg-emerald-50/30 border-emerald-300 ring-2 ring-emerald-500/20"
                            : "bg-white border-slate-200"
                            }`}
                        >
                          <div>
                            {isBestPrice && (
                              <span className="inline-block bg-emerald-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-full mb-2">
                                ★ Meilleure Offre
                              </span>
                            )}
                            <div className="h-36 flex items-center justify-center bg-white rounded-xl mb-3 p-2">
                              {item.image_url ? (
                                <img
                                  src={item.image_url}
                                  alt={item.title}
                                  className="max-h-full object-contain"
                                />
                              ) : (
                                <span className="text-xs text-slate-400">
                                  Sans image
                                </span>
                              )}
                            </div>
                            <span className="text-xs font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                              {item.source}
                            </span>
                            <h4 className="font-semibold text-sm text-slate-900 mt-2 line-clamp-3">
                              {item.title}
                            </h4>
                          </div>

                          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                            <span className="text-base font-extrabold text-slate-900">
                              {item.price
                                ? `${item.price.toLocaleString()} ${item.currency || "FCFA"
                                }`
                                : "Non communiqué"}
                            </span>
                            <a
                              href={item.product_url}
                              target="_blank"
                              rel="noreferrer"
                              className="text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-white px-3 py-1.5 rounded-lg transition"
                            >
                              Aller sur le site
                            </a>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;