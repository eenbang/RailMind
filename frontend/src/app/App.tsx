import { useEffect, useState } from "react";
import { PreferencePanel } from "../features/recommendations/PreferencePanel";
import { RecommendationList } from "../features/recommendations/RecommendationList";
import { SearchPanel } from "../features/search/SearchPanel";
import { fetchRecommendations } from "../services/api";
import type {
  RecommendationResult,
  TravelRequest
} from "../types/api";

const defaultRequest: TravelRequest = {
  origin: "上海",
  destination: "杭州",
  departure_window: { start: "08:00", end: "12:00" },
  arrival_deadline: null,
  max_price: 100,
  max_duration_minutes: 120,
  seat_classes: ["second"],
  weights: {
    price: 0.3,
    duration: 0.35,
    comfort: 0.2,
    schedule: 0.15
  }
};

export function App() {
  const [request, setRequest] = useState(defaultRequest);
  const [result, setResult] = useState<RecommendationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function runRecommendation(nextRequest = request) {
    setLoading(true);
    setError("");
    try {
      const nextResult = await fetchRecommendations(nextRequest);
      setResult(nextResult);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "未知错误");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void runRecommendation(defaultRequest);
    // The first result seeds the framework demo with a useful state.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function updatePreferences(weights: TravelRequest["weights"]) {
    const next = { ...request, weights };
    setRequest(next);
  }

  return (
    <div className="app-shell">
      <header className="site-header">
        <a className="brand" href="/" aria-label="RailMind 首页">
          <span className="brand-mark">RM</span>
          <span>
            <strong>RailMind</strong>
            <small>铁路出行决策助手</small>
          </span>
        </a>
        <nav>
          <a className="active" href="#planner">
            出行规划
          </a>
          <a href="#how-it-works">如何决策</a>
          <span className="status-pill">MVP 框架</span>
        </nav>
      </header>

      <main id="planner">
        <section className="hero">
          <div>
            <p className="eyebrow">不是更多车次，而是更清楚的选择</p>
            <h1>
              找到与你
              <em>想法一致</em>
              的那班车
            </h1>
            <p className="hero-copy">
              RailMind 会把价格、时间与舒适度放在同一张“决策尺”上，
              让推荐结果不只告诉你“是什么”，也说明“为什么”。
            </p>
          </div>
          <div className="hero-stamp" aria-label="推荐引擎版本">
            <span>WEIGHTED</span>
            <strong>3</strong>
            <small>默认推荐方案</small>
          </div>
        </section>

        <div className="workspace">
          <div className="main-column">
            <SearchPanel
              request={request}
              disabled={loading}
              onChange={setRequest}
              onSearch={() => void runRecommendation()}
            />
            <RecommendationList
              request={request}
              result={result}
              loading={loading}
              error={error}
            />
          </div>

          <PreferencePanel
            weights={request.weights}
            suggestions={result?.relaxation_suggestions ?? []}
            onChange={updatePreferences}
          />
        </div>

        <section className="how-it-works" id="how-it-works">
          <div>
            <span>01</span>
            <h2>统一需求</h2>
            <p>表单和自然语言进入同一个需求模型。</p>
          </div>
          <div>
            <span>02</span>
            <h2>先过滤再评分</h2>
            <p>硬条件控制可行性，软偏好负责排序。</p>
          </div>
          <div>
            <span>03</span>
            <h2>解释每一分</h2>
            <p>不制造“最佳”，而是明确每个方案的取舍。</p>
          </div>
        </section>
      </main>
    </div>
  );
}
