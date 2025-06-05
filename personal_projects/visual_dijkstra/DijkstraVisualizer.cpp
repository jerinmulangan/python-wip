#include <SFML/Graphics.hpp>
#include <vector>
#include <queue>
#include <limits>
#include <random>
#include <chrono>
#include <fstream>
#include <iomanip>

const int WIDTH  = 800;
const int HEIGHT = 800;
const int ROWS   = 150;
const int COLS   = 150;
const int NODE_SIZE = WIDTH / COLS;
const char* CSV_FILE = "runs.csv";

struct Node {
    int   row{}, col{};
    float dist{std::numeric_limits<float>::infinity()};
    bool  visited{false};
    bool  isWall{false};
    Node* previous{nullptr};
    Node() = default;
    Node(int r, int c) : row(r), col(c) {}
    bool operator>(const Node& o) const { return dist > o.dist; }
};

std::vector<std::vector<Node>> createGrid() {
    std::vector<std::vector<Node>> g(ROWS, std::vector<Node>(COLS));
    for (int r = 0; r < ROWS; ++r)
        for (int c = 0; c < COLS; ++c)
            g[r][c] = Node(r, c);
    return g;
}

std::vector<Node*> neighbors(std::vector<std::vector<Node>>& grid, Node& n) {
    const int dr[] = {-1, 1, 0, 0};
    const int dc[] = {0, 0, -1, 1};
    std::vector<Node*> out;
    for (int i = 0; i < 4; ++i) {
        int nr = n.row + dr[i];
        int nc = n.col + dc[i];
        if (nr >= 0 && nr < ROWS && nc >= 0 && nc < COLS && !grid[nr][nc].isWall)
            out.push_back(&grid[nr][nc]);
    }
    return out;
}

void dijkstra(std::vector<std::vector<Node>>& grid, Node* start, Node* goal) {
    auto cmp = [](Node* a, Node* b) { return a->dist > b->dist; };
    std::priority_queue<Node*, std::vector<Node*>, decltype(cmp)> pq(cmp);
    start->dist = 0.f;
    pq.push(start);
    while (!pq.empty()) {
        Node* cur = pq.top(); pq.pop();
        if (cur->visited) continue;
        cur->visited = true;
        if (cur == goal) break;
        for (Node* nb : neighbors(grid, *cur)) {
            float nd = cur->dist + 1.f;
            if (nd < nb->dist) {
                nb->dist = nd;
                nb->previous = cur;
                pq.push(nb);
            }
        }
    }
}

void drawGrid(sf::RenderWindow& win, const std::vector<std::vector<Node>>& grid,
              Node* start, Node* goal) {
    sf::RectangleShape cell(sf::Vector2f(NODE_SIZE - 1.f, NODE_SIZE - 1.f));
    for (int r = 0; r < ROWS; ++r) {
        for (int c = 0; c < COLS; ++c) {
            const Node& n = grid[r][c];
            if (&n == start)      cell.setFillColor(sf::Color::Green);
            else if (&n == goal)  cell.setFillColor(sf::Color::Red);
            else if (n.isWall)    cell.setFillColor(sf::Color::Black);
            else if (n.visited)   cell.setFillColor(sf::Color(100,100,255));
            else                  cell.setFillColor(sf::Color::White);
            cell.setPosition(sf::Vector2f(static_cast<float>(c*NODE_SIZE), static_cast<float>(r*NODE_SIZE)));
            win.draw(cell);
        }
    }
    cell.setFillColor(sf::Color::Yellow);
    for (Node* p = goal; p && p->previous && p != start; p = p->previous) {
        cell.setPosition(sf::Vector2f(static_cast<float>(p->col*NODE_SIZE), static_cast<float>(p->row*NODE_SIZE)));
        win.draw(cell);
    }
}

int countVisited(const std::vector<std::vector<Node>>& grid) {
    int total = 0;
    for (const auto& row : grid)
        for (const auto& n : row)
            if (n.visited) ++total;
    return total;
}

int main() {
    sf::RenderWindow window(sf::VideoMode(sf::Vector2u(WIDTH, HEIGHT)), "Dijkstra Visualizer (SFML 3)");

    auto grid = createGrid();
    Node* start = &grid[10][10];
    Node* goal  = &grid[100][100];

    std::mt19937 rng(static_cast<unsigned>(time(nullptr)));
    std::uniform_int_distribution<int> distR(0, ROWS-1), distC(0, COLS-1);
    for (int i=0;i<2000;++i) {
        int r=distR(rng), c=distC(rng);
        if (&grid[r][c]!=start && &grid[r][c]!=goal) grid[r][c].isWall=true;
    }

    auto t0 = std::chrono::high_resolution_clock::now();
    dijkstra(grid,start,goal);
    auto t1 = std::chrono::high_resolution_clock::now();
    double ms = std::chrono::duration<double,std::milli>(t1-t0).count();
    int visited = countVisited(grid);

    std::ofstream(CSV_FILE,std::ios::app) << std::fixed<<std::setprecision(2)
        << goal->dist<<','<<visited<<','<<ms<<'\n';

    sf::Font font;
    bool showText = font.openFromFile("arial.ttf");
    sf::Text overlay(font, "", 16);
    overlay.setFillColor(sf::Color::Yellow);
    overlay.setPosition(sf::Vector2f(5.f,5.f));
    overlay.setString("Path: "+std::to_string(static_cast<int>(goal->dist))+" | Visited: "+std::to_string(visited)+" | Time: "+std::to_string(static_cast<int>(ms))+" ms");

    while (window.isOpen()) {
        if (const auto e=window.pollEvent()) if (e->is<sf::Event::Closed>()) window.close();
        window.clear();
        drawGrid(window,grid,start,goal);
        if(showText) window.draw(overlay);
        window.display();
    }
    return 0;
}
