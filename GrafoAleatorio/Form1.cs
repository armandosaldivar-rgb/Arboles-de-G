using System;
using System.Drawing;
using System.Windows.Forms;

namespace GrafoAleatorio
{
    public partial class Form1 : Form
    {
        private readonly Random random = new Random();
        private const int RADIO_NODO = 20;
        private const int MARGEN = 60;

        public Form1()
        {
            InitializeComponent();
            this.Text = "Grafo Aleatorio Simple";
            this.Size = new Size(780, 620);
            this.BackColor = Color.FromArgb(30, 30, 40);
            this.FormBorderStyle = FormBorderStyle.FixedSingle;
            this.MaximizeBox = false;

            // Botón en esquina inferior derecha
            Button btnGenerar = new Button
            {
                Text = "Nuevo grafo",
                Size = new Size(140, 45),
                Location = new Point(this.ClientSize.Width - 160, this.ClientSize.Height - 65),
                BackColor = Color.FromArgb(70, 130, 180),
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat,
                Font = new Font("Segoe UI", 11f, FontStyle.Bold)
            };
            btnGenerar.FlatAppearance.BorderSize = 0;
            btnGenerar.Click += (s, e) => this.Invalidate(); // Redibujar

            this.Controls.Add(btnGenerar);

            // Para que el botón se mantenga en la esquina al redimensionar (opcional)
            this.Resize += (s, e) =>
            {
                btnGenerar.Location = new Point(
                    this.ClientSize.Width - 160,
                    this.ClientSize.Height - 65);
            };

            // Primera generación al iniciar
            this.Paint += Form1_Paint;
        }

        private void Form1_Paint(object sender, PaintEventArgs e)
        {
            Graphics g = e.Graphics;
            g.SmoothingMode = System.Drawing.Drawing2D.SmoothingMode.AntiAlias;

            int ancho = this.ClientSize.Width;
            int alto = this.ClientSize.Height;

            // Generamos entre 6 y 15 nodos
            int cantidadNodos = random.Next(6, 16);
            PointF[] nodos = new PointF[cantidadNodos];

            // Posiciones aleatorias pero con margen
            for (int i = 0; i < cantidadNodos; i++)
            {
                int x = random.Next(MARGEN, ancho - MARGEN);
                int y = random.Next(MARGEN, alto - MARGEN - 80); // espacio para el botón
                nodos[i] = new PointF(x, y);
            }

            // Dibujamos aristas primero (para que queden detrás)
            using (Pen lapizArista = new Pen(Color.FromArgb(100, 180, 255), 1.8f))
            {
                for (int i = 0; i < cantidadNodos; i++)
                {
                    for (int j = i + 1; j < cantidadNodos; j++)
                    {
                        // Probabilidad ~30-40% de poner arista
                        if (random.NextDouble() < 0.38)
                        {
                            g.DrawLine(lapizArista, nodos[i], nodos[j]);
                        }
                    }
                }
            }

            // Dibujamos nodos encima
            using (Brush brochaNodo = new SolidBrush(Color.FromArgb(220, 80, 180)))
            using (Brush brochaTexto = new SolidBrush(Color.White))
            using (Pen bordeNodo = new Pen(Color.FromArgb(255, 100, 220), 2.5f))
            {
                for (int i = 0; i < cantidadNodos; i++)
                {
                    float x = nodos[i].X - RADIO_NODO;
                    float y = nodos[i].Y - RADIO_NODO;

                    // Círculo
                    g.FillEllipse(brochaNodo, x, y, RADIO_NODO * 2, RADIO_NODO * 2);
                    g.DrawEllipse(bordeNodo, x, y, RADIO_NODO * 2, RADIO_NODO * 2);

                    // Número del nodo (centrado)
                    string texto = (i + 1).ToString();
                    SizeF tam = g.MeasureString(texto, new Font("Segoe UI", 10f, FontStyle.Bold));
                    g.DrawString(texto,
                                 new Font("Segoe UI", 10f, FontStyle.Bold),
                                 brochaTexto,
                                 nodos[i].X - tam.Width / 2,
                                 nodos[i].Y - tam.Height / 2);
                }
            }
        }

        // Evitamos que el formulario parpadee tanto
        protected override CreateParams CreateParams
        {
            get
            {
                CreateParams cp = base.CreateParams;
                cp.ExStyle |= 0x02000000;  // WS_EX_COMPOSITED
                return cp;
            }
        }
    }
}