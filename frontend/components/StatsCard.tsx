'use client';

interface StatsCardProps {
  title: string;
  value: number;
  icon: string;
  color: 'blue' | 'purple' | 'orange' | 'green';
}

const colorClasses = {
  blue: 'bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300',
  purple: 'bg-purple-100 dark:bg-purple-900 text-purple-600 dark:text-purple-300',
  orange: 'bg-orange-100 dark:bg-orange-900 text-orange-600 dark:text-orange-300',
  green: 'bg-green-100 dark:bg-green-900 text-green-600 dark:text-green-300',
};

export default function StatsCard({ title, value, icon, color }: StatsCardProps) {
  return (
    <div className="card">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-gray-600 dark:text-gray-400 text-sm font-medium mb-2">
            {title}
          </p>
          <p className="text-3xl font-bold">{value}</p>
        </div>
        <div className={`text-3xl p-3 rounded-lg ${colorClasses[color]}`}>
          {icon}
        </div>
      </div>
    </div>
  );
}
