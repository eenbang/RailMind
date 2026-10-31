import type {
  Recommendation,
  RecommendationResult,
  TravelRequest
} from "../../types/api";

interface RecommendationListProps {
  request: TravelRequest;
  result: RecommendationResult | null;
  loading: boolean;
  error: string;
}

export function RecommendationList({
  request,
  result,
  loading,
  error
}: RecommendationListProps) {
  if (loading) {
    return <LoadingState />;
  }

  if (error) {
    return (
      <div className="empty-state surface-card">
        <span>连接异常</span>
        <h2>暂时无法获取推荐</h2>
        <p>{error}</p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="empty-state surface-card">
        <span>等待出发</span>
        <h2>先告诉我们你的选择标准</h2>
        <p>RailMind 会把看似相同的车次，解释成不同的价格、时间与舒适度取舍。</p>
      </div>
    );
  }

  if (result.recommendations.length === 0) {
    return (
      <div className="empty-state surface-card">
        <span>没有匹配</span>
        <h2>这些条件暂时互相冲突</h2>
        <p>可以参考右侧提示放宽预算、时间或座席条件。</p>
      </div>
    );
  }

  return (
    <div className="recommendation-area">
      <div className="result-summary">
        <div>
          <p className="eyebrow">推荐结果</p>
          <h2>
            {request.origin} <span>→</span> {request.destination}
          </h2>
        </div>
        <div className="result-meta">
          <strong>{result.filtered_count}</strong>
          <span>个方案符合硬条件</span>
        </div>
      </div>

      <div className="recommendation-grid">
        {result.recommendations.map((recommendation, index) => (
          <RecommendationCard
            key={recommendation.journey.id}
            rank={index + 1}
            recommendation={recommendation}
          />
        ))}
      </div>

      <ComparisonTable items={result.recommendations} />

      <p className="algorithm-note">
        {result.algorithm_version} · {result.data_version} · 展示结果用于框架演示
      </p>
    </div>
  );
}

function RecommendationCard({
  recommendation,
  rank
}: {
  recommendation: Recommendation;
  rank: number;
}) {
  const { journey } = recommendation;
  return (
    <article className={`journey-card ${rank === 1 ? "featured" : ""}`}>
      {rank === 1 && <span className="recommended-badge">首选</span>}
      <div className="journey-card-top">
        <div>
          <span className="train-number">{journey.train_no}</span>
          <span className="train-type">{journey.train_type}</span>
        </div>
        <div className="score">
          <strong>{recommendation.score}</strong>
          <span>匹配度</span>
        </div>
      </div>

      <div className="journey-time">
        <div>
          <strong>{journey.departure_time.slice(0, 5)}</strong>
          <span>{journey.departure_station}</span>
        </div>
        <div className="route-line">
          <span>{formatDuration(journey.duration_minutes)}</span>
          <i />
        </div>
        <div>
          <strong>{journey.arrival_time.slice(0, 5)}</strong>
          <span>{journey.arrival_station}</span>
        </div>
      </div>

      <div className="fare-row">
        <span>当前最低可购</span>
        <strong>¥{recommendation.selected_fare}</strong>
      </div>

      <ul className="reason-list">
        {recommendation.reasons.map((reason) => (
          <li key={reason}>{reason}</li>
        ))}
      </ul>

      <Scores recommendation={recommendation} />

      <a
        className="text-link"
        href={`https://www.12306.cn/index/`}
        target="_blank"
        rel="noreferrer"
      >
        去购票平台核验余票 ↗
      </a>
    </article>
  );
}

function Scores({ recommendation }: { recommendation: Recommendation }) {
  const scores = recommendation.dimension_scores;
  return (
    <div className="score-bars">
      <ScoreBar label="价格" value={scores.price} />
      <ScoreBar label="耗时" value={scores.duration} />
      <ScoreBar label="舒适" value={scores.comfort} />
      <ScoreBar label="时间" value={scores.schedule} />
    </div>
  );
}

function ScoreBar({ label, value }: { label: string; value: number }) {
  return (
    <div className="score-bar">
      <span>{label}</span>
      <i>
        <b style={{ width: `${value}%` }} />
      </i>
      <small>{Math.round(value)}</small>
    </div>
  );
}

function ComparisonTable({ items }: { items: Recommendation[] }) {
  return (
    <section className="comparison surface-card">
      <div className="section-heading compact">
        <p className="eyebrow">横向比较</p>
        <h2>把取舍摆在明面上</h2>
      </div>
      <div className="comparison-scroll">
        <table>
          <thead>
            <tr>
              <th>方案</th>
              <th>出发</th>
              <th>到达</th>
              <th>票价</th>
              <th>综合分</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.journey.id}>
                <td>
                  <strong>{item.journey.train_no}</strong>
                  <small>{item.journey.departure_station}</small>
                </td>
                <td>{item.journey.departure_time.slice(0, 5)}</td>
                <td>{item.journey.arrival_time.slice(0, 5)}</td>
                <td>¥{item.selected_fare}</td>
                <td>{item.score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function LoadingState() {
  return (
    <div className="loading-state surface-card">
      <div className="loading-orbit" />
      <h2>正在权衡价格与时间</h2>
      <p>对候选车次进行硬过滤、归一化评分和解释组装。</p>
    </div>
  );
}

function formatDuration(minutes: number) {
  const hours = Math.floor(minutes / 60);
  const rest = minutes % 60;
  return `${hours ? `${hours}时` : ""}${rest}分`;
}
