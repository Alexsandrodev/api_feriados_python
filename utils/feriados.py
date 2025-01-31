import datetime

class FeriadosMoveis:
    def __init__(self, ano):
        self.ano = ano
        self.pascoa = self.calcular_pascoa()
        self.feriados = self.get_feriados()


    def calcular_pascoa(self):
        """
            calcula a data da pascoa, de acordo com o ano passar e retorna o mês e o dia da pascoa.

        Args:
            ano: ano ao qual sera calculado o feriado da Páscoa.

        retuns:
            Uma string com o mês e a data da pascoa no ano pedido.
        """
        
        a = self.ano % 19
        b = self.ano // 100
        c = self.ano % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        mes = (h + l - 7 * m + 114) // 31
        dia =  1 + ((h + l - 7 * m + 114) % 31)

        if mes <=9:
            return f"0{mes}-{dia}"
        else:
            return f"{mes}-{dia}"
            
    
    def get_pascoa(self):
        """
            Retorna a data da Páscoa previamente calculada.
            
            Return:
                string: data da pascoa
        """
        return self.pascoa
 

    def calcular_feriado(self, dias):
        """
            Recebe um número de dias como parâmetro e calcula a data de um feriado com base na data da Páscoa.

            Args:
                data (int): data de dias para somar ou subtrair os dias

            Return:
                strind: (MM-DD) mes e dia do feriado movel pedido
        """

        pascoa = f'{self.ano}-{self.pascoa}'

        pascoa = datetime.datetime.strptime(pascoa, "%Y-%m-%d")
        feriado = pascoa + datetime.timedelta(days=dias)
        
        feriado = feriado.strftime("%m-%d")
        return feriado

    def get_feriados(self):
        """
            Retorna um dicionário com os feriados móveis calculados, incluindo a data e o nome de cada feriado.

            Return:
                Dict: dicionario com os feirados moveis de determindao ano.
        """

        feriados = {}

        feriados[self.pascoa] = { "name" : "Pascoa"}
        feriados[self.calcular_feriado(-47)] = { "name" : "Carnaval"}
        feriados[self.calcular_feriado(60)] = { "name" : "Corpus Christi"}
        feriados[self.calcular_feriado(-2)] = { "name" : "Sexta-Feira Santa"}

        return feriados
    

