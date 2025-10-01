import React, { useState, useEffect, useCallback, memo } from 'react';
import { Menu, X, Search, Filter, MoreVertical, ChevronDown, ChevronUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';

// 移动端导航组件
interface MobileNavigationProps {
  items: {
    id: string;
    label: string;
    icon: React.ReactNode;
    href?: string;
    onClick?: () => void;
    badge?: string | number;
  }[];
  currentPath?: string;
}

export const MobileNavigation = memo(({ items, currentPath }: MobileNavigationProps) => {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <>
      {/* 移动端顶部导航栏 */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 bg-white border-b shadow-sm">
        <div className="flex items-center justify-between p-4">
          <h1 className="text-xl font-bold">舆情分析系统</h1>
          <Sheet open={isOpen} onOpenChange={setIsOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="sm">
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-80">
              <div className="flex flex-col space-y-4 mt-6">
                {items.map(item => (
                  <Button
                    key={item.id}
                    variant={currentPath === item.href ? "default" : "ghost"}
                    className="justify-start h-12"
                    onClick={() => {
                      item.onClick?.();
                      if (item.href) {
                        window.location.href = item.href;
                      }
                      setIsOpen(false);
                    }}
                  >
                    <div className="flex items-center space-x-3 w-full">
                      {item.icon}
                      <span className="flex-1 text-left">{item.label}</span>
                      {item.badge && (
                        <span className="bg-red-500 text-white text-xs rounded-full px-2 py-1">
                          {item.badge}
                        </span>
                      )}
                    </div>
                  </Button>
                ))}
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
      
      {/* 移动端底部导航栏 */}
      <div className="lg:hidden fixed bottom-0 left-0 right-0 z-50 bg-white border-t shadow-lg">
        <div className="grid grid-cols-4 gap-1 p-2">
          {items.slice(0, 4).map(item => (
            <Button
              key={item.id}
              variant="ghost"
              className={`flex flex-col items-center space-y-1 h-16 ${
                currentPath === item.href ? 'text-blue-600 bg-blue-50' : 'text-gray-600'
              }`}
              onClick={() => {
                item.onClick?.();
                if (item.href) {
                  window.location.href = item.href;
                }
              }}
            >
              {item.icon}
              <span className="text-xs">{item.label}</span>
              {item.badge && (
                <span className="absolute top-1 right-1 bg-red-500 text-white text-xs rounded-full h-4 w-4 flex items-center justify-center">
                  {item.badge}
                </span>
              )}
            </Button>
          ))}
        </div>
      </div>
    </>
  );
});

// 移动端搜索组件
interface MobileSearchProps {
  placeholder?: string;
  onSearch: (query: string) => void;
  filters?: {
    id: string;
    label: string;
    options: { value: string; label: string }[];
  }[];
  onFilterChange?: (filterId: string, value: string) => void;
}

export const MobileSearch = memo(({ 
  placeholder = "搜索...", 
  onSearch, 
  filters = [],
  onFilterChange 
}: MobileSearchProps) => {
  const [query, setQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [activeFilters, setActiveFilters] = useState<Record<string, string>>({});
  
  const handleSearch = useCallback(() => {
    onSearch(query);
  }, [query, onSearch]);
  
  const handleFilterChange = useCallback((filterId: string, value: string) => {
    setActiveFilters(prev => ({ ...prev, [filterId]: value }));
    onFilterChange?.(filterId, value);
  }, [onFilterChange]);
  
  return (
    <div className="space-y-3">
      {/* 搜索输入框 */}
      <div className="flex space-x-2">
        <div className="flex-1 relative">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={placeholder}
            className="pr-10"
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <Button
            size="sm"
            className="absolute right-1 top-1 h-8 w-8 p-0"
            onClick={handleSearch}
          >
            <Search className="h-4 w-4" />
          </Button>
        </div>
        
        {filters.length > 0 && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
            className="px-3"
          >
            <Filter className="h-4 w-4" />
          </Button>
        )}
      </div>
      
      {/* 过滤器 */}
      {showFilters && filters.length > 0 && (
        <Card>
          <CardContent className="p-4 space-y-3">
            {filters.map(filter => (
              <div key={filter.id}>
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  {filter.label}
                </label>
                <select
                  value={activeFilters[filter.id] || ''}
                  onChange={(e) => handleFilterChange(filter.id, e.target.value)}
                  className="w-full p-2 border rounded-md"
                >
                  <option value="">全部</option>
                  {filter.options.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
});

// 移动端卡片列表
interface MobileCardListProps {
  items: any[];
  renderCard: (item: any, index: number) => React.ReactNode;
  loading?: boolean;
  onLoadMore?: () => void;
  hasMore?: boolean;
  emptyMessage?: string;
}

export const MobileCardList = memo(({ 
  items, 
  renderCard, 
  loading = false,
  onLoadMore,
  hasMore = false,
  emptyMessage = "暂无数据"
}: MobileCardListProps) => {
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  
  const handleLoadMore = useCallback(async () => {
    if (isLoadingMore || !hasMore) return;
    
    setIsLoadingMore(true);
    try {
      await onLoadMore?.();
    } finally {
      setIsLoadingMore(false);
    }
  }, [isLoadingMore, hasMore, onLoadMore]);
  
  // 无限滚动检测
  useEffect(() => {
    if (!hasMore || !onLoadMore) return;
    
    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
      if (scrollTop + clientHeight >= scrollHeight - 1000) {
        handleLoadMore();
      }
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [handleLoadMore, hasMore, onLoadMore]);
  
  if (loading && items.length === 0) {
    return (
      <div className="space-y-3">
        {[...Array(5)].map((_, i) => (
          <Card key={i}>
            <CardContent className="p-4">
              <div className="space-y-3">
                <div className="h-4 bg-gray-200 rounded animate-pulse" />
                <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4" />
                <div className="h-4 bg-gray-200 rounded animate-pulse w-1/2" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }
  
  if (items.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <p className="text-gray-500">{emptyMessage}</p>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <div className="space-y-3">
      {items.map((item, index) => renderCard(item, index))}
      
      {hasMore && (
        <div className="text-center py-4">
          {isLoadingMore ? (
            <div className="flex items-center justify-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500" />
              <span className="text-sm text-gray-500">加载中...</span>
            </div>
          ) : (
            <Button variant="outline" onClick={handleLoadMore}>
              加载更多
            </Button>
          )}
        </div>
      )}
    </div>
  );
});

// 移动端操作菜单
interface MobileActionMenuProps {
  actions: {
    id: string;
    label: string;
    icon: React.ReactNode;
    onClick: () => void;
    destructive?: boolean;
    disabled?: boolean;
  }[];
  trigger?: React.ReactNode;
}

export const MobileActionMenu = memo(({ actions, trigger }: MobileActionMenuProps) => {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <Sheet open={isOpen} onOpenChange={setIsOpen}>
      <SheetTrigger asChild>
        {trigger || (
          <Button variant="ghost" size="sm">
            <MoreVertical className="h-4 w-4" />
          </Button>
        )}
      </SheetTrigger>
      <SheetContent side="bottom" className="h-auto">
        <div className="grid gap-2 py-4">
          {actions.map(action => (
            <Button
              key={action.id}
              variant={action.destructive ? "destructive" : "ghost"}
              className="justify-start h-12"
              disabled={action.disabled}
              onClick={() => {
                action.onClick();
                setIsOpen(false);
              }}
            >
              <div className="flex items-center space-x-3">
                {action.icon}
                <span>{action.label}</span>
              </div>
            </Button>
          ))}
        </div>
      </SheetContent>
    </Sheet>
  );
});

// 移动端折叠面板
interface MobileCollapsibleProps {
  title: string;
  children: React.ReactNode;
  defaultExpanded?: boolean;
  badge?: string | number;
}

export const MobileCollapsible = memo(({ 
  title, 
  children, 
  defaultExpanded = false,
  badge 
}: MobileCollapsibleProps) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  
  return (
    <Card>
      <CardHeader 
        className="cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CardTitle className="text-base">{title}</CardTitle>
            {badge && (
              <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                {badge}
              </span>
            )}
          </div>
          {isExpanded ? (
            <ChevronUp className="h-4 w-4" />
          ) : (
            <ChevronDown className="h-4 w-4" />
          )}
        </div>
      </CardHeader>
      {isExpanded && (
        <CardContent className="pt-0">
          {children}
        </CardContent>
      )}
    </Card>
  );
});

// 移动端手势支持Hook
export const useSwipeGesture = ({
  onSwipeLeft,
  onSwipeRight,
  onSwipeUp,
  onSwipeDown,
  threshold = 50
}: {
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  threshold?: number;
}) => {
  const [touchStart, setTouchStart] = useState<{ x: number; y: number } | null>(null);
  
  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    const touch = e.touches[0];
    setTouchStart({ x: touch.clientX, y: touch.clientY });
  }, []);
  
  const handleTouchEnd = useCallback((e: React.TouchEvent) => {
    if (!touchStart) return;
    
    const touch = e.changedTouches[0];
    const deltaX = touch.clientX - touchStart.x;
    const deltaY = touch.clientY - touchStart.y;
    
    const absDeltaX = Math.abs(deltaX);
    const absDeltaY = Math.abs(deltaY);
    
    if (absDeltaX > threshold && absDeltaX > absDeltaY) {
      // 水平滑动
      if (deltaX > 0) {
        onSwipeRight?.();
      } else {
        onSwipeLeft?.();
      }
    } else if (absDeltaY > threshold && absDeltaY > absDeltaX) {
      // 垂直滑动
      if (deltaY > 0) {
        onSwipeDown?.();
      } else {
        onSwipeUp?.();
      }
    }
    
    setTouchStart(null);
  }, [touchStart, threshold, onSwipeLeft, onSwipeRight, onSwipeUp, onSwipeDown]);
  
  return {
    onTouchStart: handleTouchStart,
    onTouchEnd: handleTouchEnd
  };
};

// 移动端视口检测Hook
export const useMobileViewport = () => {
  const [isMobile, setIsMobile] = useState(false);
  const [isTablet, setIsTablet] = useState(false);
  const [orientation, setOrientation] = useState<'portrait' | 'landscape'>('portrait');
  
  useEffect(() => {
    const checkViewport = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;
      
      setIsMobile(width < 768);
      setIsTablet(width >= 768 && width < 1024);
      setOrientation(height > width ? 'portrait' : 'landscape');
    };
    
    checkViewport();
    window.addEventListener('resize', checkViewport);
    window.addEventListener('orientationchange', checkViewport);
    
    return () => {
      window.removeEventListener('resize', checkViewport);
      window.removeEventListener('orientationchange', checkViewport);
    };
  }, []);
  
  return { isMobile, isTablet, orientation, isDesktop: !isMobile && !isTablet };
};